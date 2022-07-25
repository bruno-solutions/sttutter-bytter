import json
from pathlib import Path
from typing import Final

from configuration.constants import APPLICATION_NAME
from slicer import Slicer
from utility import normalize_file_path


class Template:
    configuration: Final = {
        "output_file_type": "wav",
        "work_root": str(Path.cwd()),
        "log_debug": True,
        "log_warning": True,
        "log_error": True,
        "log_to_console": True,
        "log_file_separator": "-",
        "channels": 2,  # stereo
        "sample_width": 2,  # bytes, CD Quality
        "frame_rate": 44100,  # hz, CD quality
        "downloader_module": "aria2c",
        "clips_per_stage": 10,
        "detection_window_miliseconds": 10,
        "low_threshold": -20.0,
        "drift_decibels": 0.1,
        "clip_size_miliseconds": 9000,
        "beat_count": 4,
        "attack_miliseconds": 50,
        "decay_miliseconds": 50,
        "pad_duration_miliseconds": 250,
        "fade_in_miliseconds": 500,
        "fade_out_miliseconds": 500
    }

    logic: Final = {
        "logic": [{"method": method, "active": False, "arguments": {}} for method in Slicer.get_slicer_methods()]
    }

    @staticmethod
    def generate_configuration_and_logic_template(file_path: str) -> None:
        """
        Write a configuration/logic template file with user default values with a list of all available slicer methods
        From the command line use switches -T or --template to produce a template file
        Args:
        :param file_path: the name (with or without the path) of the JSON configuration logic file to be generated
        """
        file_path = normalize_file_path(file_path, "json")

        try:
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump({"configuration": Template.configuration, "logic": Template.logic}, json_file, ensure_ascii=False, indent=4)
        except IOError as exception:
            print(f"Unable to write {APPLICATION_NAME} template configuration/logic file {file_path}")
            print(f"[ERROR]: {exception}")
            raise exception

        print(f"Created {APPLICATION_NAME} template configuration/logic file {file_path}")
