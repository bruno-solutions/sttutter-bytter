import json

from constants import configuration_constants
from derived import configuration_derived
from mutable import configuration_mutable, logic_mutable
from utility import normalize_file_path
from utility.singleton import singleton


@singleton
class Configuration(object):
    def __init__(self):
        self.constant_configuration = configuration_constants
        self.mutable_configuration = configuration_mutable
        self.derived_configuration = configuration_derived
        self.set_derived_configuration()
        self.mutable_logic = logic_mutable

    def set_configuration_value(self, key: str, value: str) -> None:
        if key in self.derived_configuration:
            print(f"Derived: configuration['{key}'] replacing value {self.derived_configuration[key]} with {value}")
            self.derived_configuration[key] = value
        elif key in self.mutable_configuration:
            print(f"Mutable: configuration['{key}'] replacing value {self.mutable_configuration[key]} with {value}")
            self.mutable_configuration[key] = value
        elif key in self.constant_configuration:
            print(f"Constant: configuration['{key}'] value for this key cannot be changed")
        else:
            print(f"Ignored: configuration['{key}'] is not recognized")

    def set_derived_configuration(self) -> None:
        self.set_configuration_value('maximum_samples', 24 * 60 * 60 * self.mutable_configuration['frame_rate'])

        work_root = self.mutable_configuration['work_root']
        log_root = f"{work_root}\\log"

        self.set_configuration_value('configuration_logic_file_path', f"{work_root}\\{self.constant_configuration['configuration_logic_file_name']}")
        self.set_configuration_value('temp_root', f"{work_root}\\temp")
        self.set_configuration_value('cache_root', f"{work_root}\\cache")
        self.set_configuration_value('export_root', f"{work_root}\\export")
        self.set_configuration_value('log_root', log_root)
        self.set_configuration_value('log_file_path', f"{log_root}\\{self.constant_configuration['application_name']}.{self.constant_configuration['log_file_type']}")
        print(self.derived_configuration)

    def set_mutable_configuration(self, configuration_and_logic: {}) -> None:
        for key, value in configuration_and_logic.items():
            self.set_configuration_value(key, value)
        self.set_derived_configuration()

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

        # command line options override loaded configuration key values

        loaded_configuration = loaded_configuration_and_logic['configuration']

        if work_root is not None:
            loaded_configuration['work_root'] = work_root

        if verbose is not None:
            loaded_configuration['log_to_console'] = verbose
            loaded_configuration['log_debug'] = verbose
            loaded_configuration['log_info'] = verbose
            loaded_configuration['log_warning'] = verbose
            loaded_configuration['log_error'] = verbose

        if debug is not None:
            loaded_configuration['log_debug'] = debug
            loaded_configuration['log_info'] = debug
            loaded_configuration['log_warning'] = debug
            loaded_configuration['log_error'] = debug

        self.set_mutable_configuration(loaded_configuration)
        self.mutable_logic = loaded_configuration_and_logic['logic']

    def get(self, key: str):
        if key in self.constant_configuration:
            return self.constant_configuration[key]
        elif key in self.mutable_configuration:
            return self.mutable_configuration[key]
        elif key in self.derived_configuration:
            return self.derived_configuration[key]
        elif 'logic' == key:
            return self.mutable_logic
        else:
            raise KeyError(f"{key} not found in the configuration parameters")
