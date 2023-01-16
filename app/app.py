"""The main module"""

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)
import sys

import tester
from audioprocessor import AudioProcessor
from cli.cli import process_command_line_arguments
from configuration.configuration import Configuration
from logger import Logger


def main():
    configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug = process_command_line_arguments()
    Configuration().load_configuration_and_logic(configuration_and_logic_file_path, work_root, verbose, debug)

    recording = AudioProcessor(preserve_cache=True)

    url = tester.source(9)

    try:
        recording.load(url)
    except FileNotFoundError:
        Logger.error(f"Unable to access {url} [Processing with next URL]")
        sys.exit(-1)

    recording.normalize()
    recording.slice()
    recording.fade()
    recording.export()


if "__main__" == __name__:
    main()
