DEBUG_AUTO_CLEAN_CACHE = False
DEBUG_LOAD_WAV_ONLY = True
DEBUG_SKIP_YTDL_POST_PROCESSING = False  # Testing .webm file
DEBUG_VERBOSE = False

DURATION = 3
THRESHOLD = 0.01
SAMPLE_RATE = 44100  # Todo: Allow files to be processed of any sample rate (currently set to 44100 in downloader)

CACHE_ROOT = "cache/"
FILE_NAME = "ytdl-fullsong"
WAV_FILE_NAME = FILE_NAME + ".wav"
WEBM_FILE_NAME = FILE_NAME + ".webm"
CACHE_FILE_NAME = CACHE_ROOT + FILE_NAME
CACHE_WAV_FILE_NAME = CACHE_ROOT + WAV_FILE_NAME
CACHE_WEBM_FILE_NAME = CACHE_ROOT + WEBM_FILE_NAME

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
