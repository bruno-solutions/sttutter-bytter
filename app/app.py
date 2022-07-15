"""The main module"""

import tester
from audioprocessor import AudioProcessor

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

methods = [
    {'method': 'slice_on_beat', 'arguments': {'beat_count': 4, 'attack_miliseconds': 50, 'max_clips': 15}},
    {'method': 'slice_at_random', 'arguments': {'pad_miliseconds': 250}},
    {'method': 'slice_on_vocal_change', 'arguments': {'detection_chunk_size_miliseconds': 20, 'low_volume_threshold_decibels': -20.0, 'volume_drift_decibels': 0.1, 'max_clips': 20}},
    {'method': 'slice_on_volume_change', 'arguments': {'detection_chunk_size_miliseconds': 10, 'low_volume_threshold_decibels': -20.0, 'volume_drift_decibels': 0.1}}
]

AudioProcessor(preserve_cache=True) \
    .download(tester.url(1)) \
    .metadata() \
    .normalize() \
    .slice(methods) \
    .fade() \
    .export()
