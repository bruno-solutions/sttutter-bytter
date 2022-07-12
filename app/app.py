"""The main module"""

from audioprocessor import AudioProcessor
from configuration import CACHE_ROOT, CACHE_WAV_FILE_NAME
from configuration import URL, DURATION, THRESHOLD, DEFAULT_SAMPLE_RATE, EXPORT_ROOT
from file import purge_files

purge_files(cache_root=CACHE_ROOT, export_root=EXPORT_ROOT)

AudioProcessor(URL, CACHE_WAV_FILE_NAME, DEFAULT_SAMPLE_RATE, slicer_name="voice", slicer_method="slice_at_voice") \
    .preprocess() \
    .slice(DURATION if not None else 9, THRESHOLD if not None else 0.01, count=5) \
    .postprocess() \
    .export(directory=EXPORT_ROOT)
