"""The main module"""

from audioprocessor import AudioProcessor
from configuration import CACHE_ROOT
from configuration import EXAMPLE_URL, DURATION, THRESHOLD, EXPORT_ROOT
from file import refresh_roots

refresh_roots(cache_root=CACHE_ROOT, export_root=EXPORT_ROOT)

AudioProcessor(EXAMPLE_URL, slicer_name="voice", slicer_method="slice_at_voice") \
    .download() \
    .metadata() \
    .normalize() \
    .slice(duration=DURATION, threshold=THRESHOLD, clip_limit=5) \
    .fade() \
    .export(directory=EXPORT_ROOT)
