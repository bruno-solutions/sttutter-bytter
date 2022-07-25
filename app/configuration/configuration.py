import json
from typing import Final

from configuration.constants import configuration_constants
from configuration.template import Template
from utility import normalize_file_path
from utility.singleton import singleton


@singleton
class Configuration:
    constant_configuration: Final = configuration_constants
    mutable_configuration: Final = Template.configuration
    mutable_logic: Final = Template.logic
    derived_configuration: Final = {}

    def __init__(self):
        self.set_derived_configuration_and_logic()

    def set_derived_configuration_and_logic(self) -> None:
        work_root = self.mutable_configuration['work_root']

        self.derived_configuration['configuration_logic_file_path'] = f"{self.mutable_configuration['work_root']}\\{self.constant_configuration['configuration_logic_file_name']}"
        self.derived_configuration['temp_root'] = f"{work_root}\\temp"
        self.derived_configuration['cache_root'] = f"{work_root}\\cache"
        self.derived_configuration['export_root'] = f"{work_root}\\export"
        self.derived_configuration['log_root'] = f"{work_root}\\log"
        self.derived_configuration['log_file_path'] = f"{self.derived_configuration['log_root']}\\{self.constant_configuration['application_name']}.{self.constant_configuration['log_file_type']}"

    def set_mutable_configuration_value(self, key: str, value: str) -> None:
        if key in self.constant_configuration:
            print(f"configuration['{key}'] is not a constant configuration key, that cannot be changed")
        elif key in self.mutable_configuration:
            print(f"configuration['{key}'] replacing value {self.mutable_configuration[key]} with {value}")
            self.mutable_configuration[key] = value
        elif key in self.derived_configuration:
            print(f"configuration['{key}'] is not a derived configuration key, that cannot be directly set")
        else:
            print(f"configuration['{key}'] is not a mutable configuration key, ignoring")

    def set_mutable_configuration(self, configuration_and_logic: {}) -> None:
        for key, value in configuration_and_logic.items():
            self.set_mutable_configuration_value(key, value)
        self.set_derived_configuration_and_logic()

    def load_configuration_and_logic(self, file_path: str = None, work_root: str = None, verbose: bool = None, debug: bool = None) -> None:
        if file_path is None:
            if work_root is None:
                file_path = f"{self.derived_configuration['configuration_logic_file_path']}"
            else:
                file_path = f"{work_root}\\{self.constant_configuration['configuration_logic_file_name']}"

        file_path = normalize_file_path(file_path, "json")

        try:
            with open(file_path) as json_file:
                loaded_configuration_and_logic: {} = json.load(json_file)
        except IOError as exception:
            print(f"Unable to open configuration/script file {file_path}")
            print(f"[ERROR]: {exception}")
            raise exception

        loaded_configuration = loaded_configuration_and_logic['configuration']
        loaded_logic = loaded_configuration_and_logic['logic']

        # command line options override loaded configuration key values 

        if work_root is not None:
            loaded_configuration['work_root'] = work_root

        if verbose is not None:
            loaded_configuration['log_to_console'] = verbose
            loaded_configuration['log_debug'] = verbose
            loaded_configuration['log_warning'] = verbose
            loaded_configuration['log_error'] = verbose

        if debug is not None:
            loaded_configuration['log_debug'] = debug
            loaded_configuration['log_warning'] = debug
            loaded_configuration['log_error'] = debug

        self.set_mutable_configuration(loaded_configuration)
        self.mutable_logic = loaded_logic

    def get(self, key: str):
        return self[key]
