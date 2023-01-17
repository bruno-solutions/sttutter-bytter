import json
import sys
from argparse import ArgumentParser

from configuration import Configuration
from utility import normalize_file_path
from configuration import configuration_mutable
from slicer import Slicer


def generate_configuration_and_logic_template(file_path: str) -> None:
    """
    Write a configuration/logic template file with user default values with a list of all available slicer methods
    From the command line use switches -T or --template to produce a template file
    Args:
    :param file_path: the name (with or without the path) of the JSON configuration logic file to be generated
    """
    template: {} = {
        "configuration": configuration_mutable,
        "logic": [
            {
                "method": method,
                "active": False,
                "weight": weight,
                "arguments": {}
            } for method, weight in Slicer.get_slicer_methods()
        ]
    }

    file_path = normalize_file_path(file_path, "json")

    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(template, json_file, ensure_ascii=False, indent=4)
    except IOError as exception:
        print(f"Unable to write {Configuration().get('application_name')} template configuration/logic file {file_path}")
        print(f"[ERROR]: {exception}")
        raise exception

    print(f"Created {Configuration().get('application_name')} template configuration/logic file {file_path}")


def load_command_line_arguments():
    parser = ArgumentParser(prog=Configuration().get('application_name'), description=Configuration().get('application_description'))
    parser.add_argument("-C", "--configuration", dest="configuration_and_logic_file", nargs="?", const=f"{Configuration().get('configuration_logic_file_path')}", help="configuration and clip logic file", metavar="xxx.json")
    parser.add_argument("-U", "--urls", dest="url_file", help="file containing an array of media file URLs", metavar="xxx.json")
    parser.add_argument("-u", "--url", dest="url", help="local file system or remote URL of a media file", metavar="file://... or http(s)://...")
    parser.add_argument("-r", "--root", dest="work_root", help="directory from which to process", metavar="local file system path")
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False, help="send debug messages to stdout")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=True, help="send debug messages to the log file")
    parser.add_argument("-t", "--template", dest="template_file", nargs="?", const=f"{Configuration().get('configuration_logic_file_path')}", help="generate a default configuration and logic template file", metavar="xxx.json")
    parser.add_argument("--version""", action="version", version=f"%(prog)s {Configuration().get('application_version')}")

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
        generate_configuration_and_logic_template(template_file)
        sys.exit(0)

    return configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug
