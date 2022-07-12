import os
import random

LOG_DEBUG = False
LOG_WARNING = True
LOG_ERROR = True
LOG_TO_CONSOLE = True
LOG_FILE = 'application.log'

DEBUG_LOAD_WAV_ONLY = True
DISABLE_DOWNLOAD_POST_PROCESSING = False

DURATION = 3
THRESHOLD = 0.01
CLIP_LIMIT = 10
DEFAULT_SAMPLE_RATE = 44100  # Todo: Allow files to be processed of any sample rate (currently set to 44100 in downloader)

AUDIO_ROOT = 'C:\\Users\\John Hart\\Desktop\\audiobot'

EXPORT_FILE_TYPE = 'wav'

DOWNLOAD_FILE_NAME = 'downloaded.audio.file'

CACHE_ROOT = AUDIO_ROOT + '\\cache'
DEFAULT_CACHE_ROOT = f"{os.getcwd()}\\cache"
CACHE_FILE_NAME = CACHE_ROOT + '\\' + DOWNLOAD_FILE_NAME
WAV_FILE_NAME = DOWNLOAD_FILE_NAME + '.' + EXPORT_FILE_TYPE
DOWNLOADED_AUDIO_FILE_NAME = CACHE_ROOT + '\\' + WAV_FILE_NAME
METADATA_FILE_NAME = CACHE_FILE_NAME + '.info.json'
EXPORT_ROOT = AUDIO_ROOT + '\\exports'
DEFAULT_EXPORT_ROOT = f"{os.getcwd()}\\export"

EXTERNAL_DOWNLOADER = 'aria2c'

EXAMPLE_URLS = [
    'https://youtu.be/Dc1-W4KsHvE',
    'https://youtu.be/oJL-lCzEXgI',
    'https://youtu.be/dQw4w9WgXcQ',
    'https://youtu.be/sZdbNMDH8hc',
    'https://youtu.be/YBSs3-RfLKk',
    'https://youtu.be/pOF_oo3EgnQ',
    'https://youtu.be/q3f9ZiH6Euw',
    'https://youtu.be/QDYRQX6FPQQ',
    'https://youtu.be/PARA6_ErZI0',
    'https://youtu.be/hOZgb0T7AM4'
]

random.seed()
EXAMPLE_URL = EXAMPLE_URLS[random.randrange(len(EXAMPLE_URLS))]
