"""The main module"""

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

import tester
from audioprocessor import AudioProcessor
from cli.cli import process_command_line_arguments
from configuration.configuration import Configuration




def main():
    configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug = process_command_line_arguments()
    Configuration().load_configuration_and_logic(configuration_and_logic_file_path, work_root, verbose, debug)

    AudioProcessor(preserve_cache=True) \
        .load(tester.source(7)) \
        .normalize() \
        .slice() \
        .fade() \
        .export()


if "__main__" == __name__:
    main()
