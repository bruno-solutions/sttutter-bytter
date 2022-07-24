import json
from pathlib import Path

from file import normalize_file_path
from slicer import Slicer

# The application decription constants

APPLICATION_AUTHOR: str = "Sttutter"
APPLICATION_NAME: str = "sttutter-bytter"
APPLICATION_VERSION: str = "0.0.1"
APPLICATION_URL: str = "bytter.sttutter.com"
APPLICATION_EMAIL: str = "bytter@sttutter.com"
APPLICATION_DESCRIPTION: str = "Artifically intelligent video and audio clipifier"

# The application configuration constants

LOADER_BASE_FILE_NAME: str  # NOT allowed to be overridden
METADATA_FILE_TYPE: str  # NOT allowed to be overridden
OUTPUT_FILE_TYPE: str  # May be overridden

WORK_ROOT: str  # May be overridden
CONFIGURATION_ROOT: str  # Derived and NOT allowed to be overridden
TEMP_ROOT: str  # Derived and NOT allowed to be overridden
CACHE_ROOT: str  # Derived and NOT allowed to be overridden
EXPORT_ROOT: str  # Derived and NOT allowed to be overridden

LOG_DEBUG: bool  # May be overridden
LOG_WARNING: bool  # May be overridden
LOG_ERROR: bool  # May be overridden
LOG_TO_CONSOLE: bool  # May be overridden

LOG_ROOT: str  # May be overridden
LOG_FILE_TYPE: str  # NOT allowed to be overridden
LOG_FILE_NAME: str  # May be overridden
DEFAULT_LOG_FILE_SEPARATOR: str  # May be overridden

DEFAULT_CHANNELS: int  # May be overridden
DEFAULT_SAMPLE_WIDTH: int  # May be overridden
DEFAULT_FRAME_RATE: int  # May be overridden
DEFAULT_DOWNLOADER_MODULE: str  # May be overridden

DEFAULT_CLIPS_PER_STAGE: int  # May be overridden
DEFAULT_DETECTION_WINDOW_MILISECONDS: int  # May be overridden
DEFAULT_LOW_THRESHOLD: float  # May be overridden
DEFAULT_DRIFT_DECIBELS: float  # May be overridden
DEFAULT_CLIP_SIZE_MILISECONDS: int  # May be overridden
DEFAULT_BEAT_COUNT: int  # May be overridden
DEFAULT_ATTACK_MILISECONDS: int  # May be overridden
DEFAULT_DECAY_MILISECONDS: int  # May be overridden
DEFAULT_PAD_DURATION_MILISECONDS: int  # May be overridden
DEFAULT_FADE_IN_MILISECONDS: int  # May be overridden
DEFAULT_FADE_OUT_MILISECONDS: int  # May be overridden

MAXIMUM_CLIP_SIZE_MILISECONDS: int  # NOT allowed to be overridden
MAXIMUM_SAMPLES: int  # NOT allowed to be overridden

LOADABLE_CONFIGURATION: {} = {
    "output_file_type": "wav",
    "work_root": Path.cwd(),
    "log_debug": True,
    "log_warning": True,
    "log_error": True,
    "log_to_console": True,
    "default_log_file_separator": "-",
    "default_channels": 2,
    "default_sample_width": 2,  # CD Quality
    "default_frame_rate": 44100,  # hz, CD quality
    "default_downloader_module": "aria2c",
    "default_clips_per_stage": 10,
    "default_detection_window_miliseconds": 10,
    "default_low_threshold": -20.0,
    "default_drift_decibels": 0.1,
    "default_clip_size_miliseconds": 9000,
    "default_beat_count": 4,
    "default_attack_miliseconds": 50,
    "default_decay_miliseconds": 50,
    "default_pad_duration_miliseconds": 250,
    "default_fade_in_miliseconds": 500,
    "default_fade_out_miliseconds": 500
}


def set_configuration_constants() -> None:
    global WORK_ROOT, CONFIGURATION_ROOT, TEMP_ROOT, CACHE_ROOT, EXPORT_ROOT, LOADER_BASE_FILE_NAME, METADATA_FILE_TYPE, OUTPUT_FILE_TYPE
    LOADER_BASE_FILE_NAME = f"{APPLICATION_NAME}.media.download"
    METADATA_FILE_TYPE = "info.json"
    OUTPUT_FILE_TYPE = LOADABLE_CONFIGURATION['output_file_type']

    WORK_ROOT = LOADABLE_CONFIGURATION['work_root']
    CONFIGURATION_ROOT = f"{WORK_ROOT}\\config"
    TEMP_ROOT = f"{WORK_ROOT}\\temp"
    CACHE_ROOT = f"{WORK_ROOT}\\cache"
    EXPORT_ROOT = f"{WORK_ROOT}\\export"

    global LOG_DEBUG, LOG_WARNING, LOG_ERROR, LOG_TO_CONSOLE
    LOG_DEBUG = LOADABLE_CONFIGURATION['log_debug']
    LOG_WARNING = LOADABLE_CONFIGURATION['log_warning']
    LOG_ERROR = LOADABLE_CONFIGURATION['log_error']
    LOG_TO_CONSOLE = LOADABLE_CONFIGURATION['log_to_console']

    global LOG_ROOT, LOG_FILE_TYPE, LOG_FILE_NAME, DEFAULT_LOG_FILE_SEPARATOR
    LOG_ROOT = f"{WORK_ROOT}\\log"
    LOG_FILE_TYPE = "log"
    LOG_FILE_NAME = f"{LOG_ROOT}\\{APPLICATION_NAME}.{LOG_FILE_TYPE}"
    DEFAULT_LOG_FILE_SEPARATOR = LOADABLE_CONFIGURATION['default_log_file_separator']

    global DEFAULT_CHANNELS, DEFAULT_SAMPLE_WIDTH, DEFAULT_FRAME_RATE, DEFAULT_DOWNLOADER_MODULE
    DEFAULT_CHANNELS = LOADABLE_CONFIGURATION['default_channels']
    DEFAULT_SAMPLE_WIDTH = LOADABLE_CONFIGURATION['default_sample_width']
    DEFAULT_FRAME_RATE = LOADABLE_CONFIGURATION['default_frame_rate']
    DEFAULT_DOWNLOADER_MODULE = LOADABLE_CONFIGURATION['default_downloader_module']

    global DEFAULT_CLIPS_PER_STAGE, DEFAULT_DETECTION_WINDOW_MILISECONDS, DEFAULT_LOW_THRESHOLD, DEFAULT_DRIFT_DECIBELS, DEFAULT_CLIP_SIZE_MILISECONDS, DEFAULT_BEAT_COUNT, DEFAULT_ATTACK_MILISECONDS, DEFAULT_DECAY_MILISECONDS, DEFAULT_PAD_DURATION_MILISECONDS, DEFAULT_FADE_IN_MILISECONDS, DEFAULT_FADE_OUT_MILISECONDS
    DEFAULT_CLIPS_PER_STAGE = LOADABLE_CONFIGURATION['default_clips_per_stage']
    DEFAULT_DETECTION_WINDOW_MILISECONDS = LOADABLE_CONFIGURATION['default_detection_window_miliseconds']
    DEFAULT_LOW_THRESHOLD = LOADABLE_CONFIGURATION['default_low_threshold']
    DEFAULT_DRIFT_DECIBELS = LOADABLE_CONFIGURATION['default_drift_decibels']
    DEFAULT_CLIP_SIZE_MILISECONDS = LOADABLE_CONFIGURATION['default_clip_size_miliseconds']
    DEFAULT_BEAT_COUNT = LOADABLE_CONFIGURATION['default_beat_count']
    DEFAULT_ATTACK_MILISECONDS = LOADABLE_CONFIGURATION['default_attack_miliseconds']
    DEFAULT_DECAY_MILISECONDS = LOADABLE_CONFIGURATION['default_decay_miliseconds']
    DEFAULT_PAD_DURATION_MILISECONDS = LOADABLE_CONFIGURATION['default_pad_duration_miliseconds']
    DEFAULT_FADE_IN_MILISECONDS = LOADABLE_CONFIGURATION['default_fade_in_miliseconds']
    DEFAULT_FADE_OUT_MILISECONDS = LOADABLE_CONFIGURATION['default_fade_out_miliseconds']

    global MAXIMUM_CLIP_SIZE_MILISECONDS, MAXIMUM_SAMPLES
    MAXIMUM_CLIP_SIZE_MILISECONDS = 27000
    MAXIMUM_SAMPLES = 24 * 60 * 60 * DEFAULT_FRAME_RATE


set_configuration_constants()


def override_configuration_setting(key: str, value) -> None:
    print(f"Replacing configuration['{key}'] == {LOADABLE_CONFIGURATION[key]} with {value}")
    LOADABLE_CONFIGURATION[key] = value


def load_configuration_script(file_path: str, work_root: str = None, verbose: bool = None, debug: bool = None) -> None:
    file_path = normalize_file_path(file_path, "json")

    try:
        with open(file_path) as json_file:
            loaded_configuration: {} = json.load(json_file)
    except IOError as exception:
        print(f"Unable to open configuration/script file {file_path}")
        print(f"[ERROR]: {exception}")
        raise exception

    # only set configuration keys that are defined in the loadable configuration

    for key, value in loaded_configuration.items():
        if key in LOADABLE_CONFIGURATION:
            override_configuration_setting(key, value)
        else:
            print(f"Ignoring unrecognmized configuration['{key}'] == {value}")

    # set configuration key based upon command line options

    if work_root is not None:
        override_configuration_setting('work_root', work_root)

    if verbose is not None:
        override_configuration_setting('log_to_console', verbose)
        override_configuration_setting('log_debug', verbose)
        override_configuration_setting('log_warning', verbose)
        override_configuration_setting('log_error', verbose)

    if debug is not None:
        override_configuration_setting('log_debug', debug)
        override_configuration_setting('log_warning', debug)
        override_configuration_setting('log_error', debug)

    set_configuration_constants()


def generate_configuration_and_logic_file(file_path: str, configuration: {} = None, logic: {} = None) -> None:
    """
    Write a configuration/logic file based upon the current application settings
    Can be used to generate a vanilla template using the -T or --template command line switch
    Args:
    :param file_path:     the name of the JSON configuration logic file to be generated
    :param configuration: an object that contains application configuration values
    :param logic:         an object that contains a slicing method sequence and method argument values
    """
    configuration_and_logic: {} = {
        "configuration": LOADABLE_CONFIGURATION if configuration is None else configuration,
        "logic": [{"method": method, "arguments": {}} for method in Slicer.get_slicer_methods()] if logic is None else logic
    }

    file_path = normalize_file_path(file_path, "json")

    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(configuration_and_logic, json_file, ensure_ascii=False, indent=4)
    except IOError as exception:
        print(f"Unable to write {APPLICATION_NAME} template configuration/logic file {file_path}")
        print(f"[ERROR]: {exception}")
        raise exception

    print(f"Created {APPLICATION_NAME} template configuration/logic file {file_path}")
