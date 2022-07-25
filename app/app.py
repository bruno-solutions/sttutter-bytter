"""The main module"""

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

import sys
from argparse import ArgumentParser

import tester
from audioprocessor import AudioProcessor
from configuration.configuration import Configuration
from configuration.template import Template

CONFIGURATION = Configuration()


def load_command_line_arguments():
    parser = ArgumentParser(prog=CONFIGURATION.get('application_name'), description=CONFIGURATION.get('application_description'))
    parser.add_argument("-C", "--configuration", dest="configuration_and_logic_file", nargs="?", const=f"{CONFIGURATION.get('configuration_logic_file_path')}", help="configuration and clip logic file", metavar="xxx.json")
    parser.add_argument("-U", "--urls", dest="url_file", help="file containing an array of media file URLs", metavar="xxx.json")
    parser.add_argument("-u", "--url", dest="url", help="local file system or remote URL of a media file", metavar="file://... or http(s)://...")
    parser.add_argument("-r", "--root", dest="work_root", help="directory from which to process", metavar="local file system path")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_false", default=False, help="send debug messages to stdout")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=True, help="send debug messages to the log file")
    parser.add_argument("-t", "--template", dest="template_file", nargs="?", const=f"{CONFIGURATION.get('configuration_logic_file_path')}", help="generate a default configuration and logic template file", metavar="xxx.json")
    parser.add_argument("--version""", action="version", version=f"%(prog)s {CONFIGURATION.get('application_version')}")

    try:
        args = vars(parser.parse_args())
    except Exception as exception:
        print(f"Command line parameter {exception}")
        sys.exit(-1)

    return args['configuration_and_logic_file'], args['url_file'], args['url'], args['work_root'], args['verbose'], args['debug'], args['template_file']


def process_command_line_arguments():
    configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug, template_file = load_command_line_arguments()

    print(configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug, template_file)

    if template_file:
        Template.generate_configuration_and_logic_template(template_file)
        sys.exit(0)

    return configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug


def main():
    configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug = process_command_line_arguments()

    CONFIGURATION.load_configuration_and_logic(configuration_and_logic_file_path, work_root, verbose, debug)

    AudioProcessor(preserve_cache=True) \
        .load(tester.source(7)) \
        .normalize() \
        .slice() \
        .fade() \
        .export()


if "__main__" == __name__:
    main()
