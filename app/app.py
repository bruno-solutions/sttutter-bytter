"""The main module"""

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

import tester
from audioprocessor import AudioProcessor
from audioprocessor import voice
from cli.cli import process_command_line_arguments
from configuration.configuration import Configuration
from logger import Logger


def main():
    configuration_and_logic_file_path, url_file_path, url, work_root, verbose, debug = process_command_line_arguments()
    Configuration().load_configuration_and_logic(configuration_and_logic_file_path, work_root, verbose, debug)

    recording = AudioProcessor(preserve_cache=True)

    url = tester.source(12)

    voice.decompose(url)

    try:
        recording.load(url)
    except:
        Logger.error(f"Unable to access {url} [Processing with next URL]")
        print("Failed while loading source")
        exit(-5)

    try:
        recording.normalize()
    except:
        print("Failed while normalizing source")
        exit(-4)

    try:
        recording.slice()
    except:
        print("Failed while slicing clips")
        exit(-3)

    try:
        recording.fade()
    except:
        print("Failed while applying clip fade-in and fade-out")
        exit(-2)

    try:
        recording.export()
    except:
        print("Failed during export")
        exit(-1)

    print("Succeeded")
    exit(0)


if "__main__" == __name__:
    main()
