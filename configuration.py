DEBUG_AUTO_CLEAN_CACHE = False
DEBUG_LOAD_WAV_ONLY = True
DEBUG_SKIP_YTDL_POST_PROCESSING = False  # Testing .webm file
DEBUG_VERBOSE = False

DURATION = 3
THRESHOLD = 0.01
SAMPLE_RATE = 44100  # Todo: Allow files to be processed of any sample rate (currently set to 44100 in downloader)

EXPORT_ROOT = "exports/"
EXPORT_FILE_TYPE = "wav"
CACHE_ROOT = "cache/"
FILE_NAME = "downloaded.audio.file"
WAV_FILE_NAME = FILE_NAME + "." + EXPORT_FILE_TYPE
WEBM_FILE_NAME = FILE_NAME + ".webm"
CACHE_FILE_NAME = CACHE_ROOT + FILE_NAME
CACHE_WAV_FILE_NAME = CACHE_ROOT + WAV_FILE_NAME
CACHE_WEBM_FILE_NAME = CACHE_ROOT + WEBM_FILE_NAME
YOUTUBE_DL_INFO_FILE_NAME = CACHE_FILE_NAME + '.info.json'

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
