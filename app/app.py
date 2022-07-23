"""The main module"""
from argparse import ArgumentParser

import tester
from audioprocessor import AudioProcessor
from configuration import APPLICATION_NAME, APPLICATION_VERSION, APPLICATION_DESCRIPTION

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
    parser.add_argument("-P", "--processor", dest="processor_file_name", help="file containing a clipification rule sequence", metavar="xxx.json")
    parser.add_argument("-U", "--urls", dest="url_file_name", help="file containing an array of media file URLs", metavar="xxx.json")
    parser.add_argument("-u", "--url", dest="url", help="local file system or remote URL of a media file", metavar="file://... or http(s)://...")
    parser.add_argument("-c", "--config", dest="cfg_file_name", help="file containing configuration settings", metavar="xxx.json")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_false", default=False, help="send debug messages to stdout")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=True, help="send debug messages to the log file")
    parser.add_argument("--version""", action="version", version=f"%(prog)s {APPLICATION_VERSION}")
    args = vars(parser.parse_args())

    return args['processor_file_name'], args['url_file_name'], args['url'], args['cfg_file_name'],args['verbose'], args['debug']


def main():
    processor_file_name, url_file_name, url, cfg_file_name, verbose, debug = load_command_line_arguments()

    print(processor_file_name, url_file_name, url, verbose, debug)

    AudioProcessor(preserve_cache=True) \
        .load(tester.source(7)) \
        .normalize() \
        .slice(methods) \
        .fade() \
        .export()


if __name__ == "__main__":
    main()
