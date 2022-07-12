"""The main module"""

from audioprocessor import AudioProcessor
from configuration import CACHE_ROOT
from configuration import EXAMPLE_URL, DURATION, THRESHOLD, EXPORT_ROOT
from file import refresh_roots

refresh_roots(cache_root=CACHE_ROOT, export_root=EXPORT_ROOT)

slicers = {'voice': 'slice_at_voice', 'volume': 'slice_at_volume_change'}

AudioProcessor(EXAMPLE_URL, slicers) \
    .download() \
    .metadata() \
    .normalize() \
    .slice(duration=DURATION, threshold=THRESHOLD, clip_limit=5) \
    .fade() \
    .export(directory=EXPORT_ROOT)
