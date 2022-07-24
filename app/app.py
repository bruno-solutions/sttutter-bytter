"""The main module"""
from argparse import ArgumentParser

import tester
from audioprocessor import AudioProcessor
from configuration import APPLICATION_NAME, APPLICATION_VERSION, APPLICATION_DESCRIPTION, load_configuration_script, generate_configuration_and_logic_file

methods: [{}] = [
    # {'method': 'slice_at_random'},
    # {'method': 'slice_at_random', 'arguments': {'clips': 2}},
    # {'method': 'slice_at_random', 'arguments': {'clip_size': '9000 ms', 'clips': 3}},
    # {'method': 'slice_at_random', 'arguments': {'begin': '2 seconds', 'clip_size': '9000 ms', 'clips': 4}},
    # {'method': 'slice_at_random', 'arguments': {'begin': '1111ms', 'end': '88%', 'clip_size': '15500 ms', 'clips': 5}},
    # {'method': 'slice_at_interval', 'arguments': {'begin': 0, 'end': 1, 'clip_size': '7500 ms', 'clips': 7}},
    # {'method': 'slice_on_beat', 'arguments': {'begin': 0, 'end': 1, 'beats': 4, 'attack': '25ms', 'decay': 75, 'clips': 15}},
    # {'method': 'slice_on_volume_change', 'arguments': {'begin': 0, 'end': 1, 'detection_window': 10, 'low_threshold': -20.0, 'drift': 0.1}},
    {'method': 'slice_on_vocal_change', 'arguments': {'begin': 0, 'end': 1, 'passes': 1, 'model': 'spleeter:5stems-16kHz', 'detection_window': 20, 'low_threshold': -20.0, 'drift': 0.1, 'clips': 20}}
]


# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

def load_command_line_arguments():
    parser = ArgumentParser(prog=APPLICATION_NAME, description=APPLICATION_DESCRIPTION)
    parser.add_argument("-C", "--configuration", dest="configuration_and_logic_file", help="configuration and clip logic file", metavar="xxx.json")
    parser.add_argument("-U", "--urls", dest="url_file", help="file containing an array of media file URLs", metavar="xxx.json")
    parser.add_argument("-u", "--url", dest="url", help="local file system or remote URL of a media file", metavar="file://... or http(s)://...")
    parser.add_argument("-r", "--root", dest="work_root", help="directory from which to process", metavar="local file system path")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_false", default=False, help="send debug messages to stdout")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=True, help="send debug messages to the log file")
    parser.add_argument("-t", "--template", dest="template_file", action="store_true", default=True, help="generate a default configuration and logic template file", metavar="xxx.json")
    parser.add_argument("--version""", action="version", version=f"%(prog)s {APPLICATION_VERSION}")
    args = vars(parser.parse_args())

    return args['configuration_and_logic_file'], args['url_file'], args['url'], args['work_root'], args['verbose'], args['debug'], args['template_file']


def main():
    configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug, template_file = load_command_line_arguments()

    if template_file:
        generate_configuration_and_logic_file(template_file)
        return

    load_configuration_script(configuration_and_logic_file_path, work_root, verbose, debug)

    print(configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug, template_file)

    AudioProcessor(preserve_cache=True) \
        .load(tester.source(7)) \
        .normalize() \
        .slice(methods) \
        .fade() \
        .export()


if __name__ == "__main__":
    main()
