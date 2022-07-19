"""The main module"""

import tester
from audioprocessor import AudioProcessor

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

methods = [
    {'method': 'slice_at_interval', 'arguments': {'begin': 0, 'end': 1, 'clip_size': '7500 ms', 'clips': 7}},
    # {'method': 'slice_on_vocal_change', 'arguments': {'begin': 0, 'end': 1, 'passes': 1, 'model': 'spleeter:5stems-16kHz', 'detection_chunk_size_miliseconds': 20, 'low_volume_threshold_decibels': -20.0, 'volume_drift_decibels': 0.1, 'clips': 20}},
    # {'method': 'slice_on_volume_change', 'arguments': {'begin': 0, 'end': 1, 'detection_chunk_size_miliseconds': 10, 'low_volume_threshold_decibels': -20.0, 'volume_drift_decibels': 0.1}},
    # {'method': 'slice_on_beat', 'arguments': {'begin': 0, 'end': 1, 'beat_count': 4, 'attack_miliseconds': 50, 'clips': 15}},
    # {'method': 'slice_at_random', 'arguments': {'begin': 0, 'end': 1, 'pad_miliseconds': 250}}
]

AudioProcessor(preserve_cache=True) \
    .download(tester.source(1)) \
    .normalize() \
    .slice(methods) \
    .fade() \
    .export()
