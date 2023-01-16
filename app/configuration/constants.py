# The application description global constants
import os
from pathlib import Path
from typing import Final

APPLICATION_AUTHOR: Final = "Sttutter"
APPLICATION_NAME: Final = "bytter"
APPLICATION_VERSION: Final = "0.0.1"
APPLICATION_URL: Final = "bytter.sttutter.com"
APPLICATION_EMAIL: Final = "bytter@sttutter.com"
APPLICATION_DESCRIPTION: Final = "Artificially intelligent video and audio clipifier"

CONFIGURATION_LOGIC_FILE_NAME: Final = f"{APPLICATION_NAME}.configuration.json"
CONFIGURATION_LOGIC_FILE_PATH: Final = f"{Path(os.getcwd()).joinpath(CONFIGURATION_LOGIC_FILE_NAME)}"

LOG_FILE_TYPE: Final = "log"
LOADER_BASE_FILE_NAME: Final = f"{APPLICATION_NAME}.media.download"
METADATA_FILE_TYPE: Final = "info.json"

MINIMUM_RECORDING_SIZE_MILLISECONDS: Final = int(1000)
MINIMUM_CLIP_SIZE_MILLISECONDS: Final = int(250)
MAXIMUM_CLIP_SIZE_MILLISECONDS: Final = int(27000)

configuration_constants: Final = {
    "application_author": APPLICATION_AUTHOR,
    "application_name": APPLICATION_NAME,
    "application_version": APPLICATION_VERSION,
    "application_url": APPLICATION_URL,
    "application_email": APPLICATION_EMAIL,
    "application_description": APPLICATION_DESCRIPTION,
    "configuration_logic_file_name": CONFIGURATION_LOGIC_FILE_NAME,
    "log_file_type": LOG_FILE_TYPE,
    "loader_base_file_name": LOADER_BASE_FILE_NAME,
    "metadata_file_type": METADATA_FILE_TYPE,
    "minimum_recording_size_milliseconds": MINIMUM_RECORDING_SIZE_MILLISECONDS,
    "minimum_clip_size_milliseconds": MINIMUM_CLIP_SIZE_MILLISECONDS,
    "maximum_clip_size_milliseconds": MAXIMUM_CLIP_SIZE_MILLISECONDS
}
