"""The main module"""

import tester
from audioprocessor import AudioProcessor

slicers = {
    'voice': 'slice_at_voice',
    # 'volume': 'slice_at_volume_change'
}

AudioProcessor(preserve_cache=True) \
    .download(tester.url(6)) \
    .metadata() \
    .normalize() \
    .get_clips(slicers) \
    .fade() \
    .export()
