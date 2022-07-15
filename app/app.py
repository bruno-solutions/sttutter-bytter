"""The main module"""

import tester
from audioprocessor import AudioProcessor
from configuration import DEFAULT_MAX_CLIPS

methods = [
    {'method': 'slice_on_beat', 'arguments': {'beat_count': [4], 'attack_miliseconds': 50, 'max_clips': DEFAULT_MAX_CLIPS}},
    {'method': 'slice_at_random', 'arguments': {'pad_miliseconds': 250, 'max_clips': DEFAULT_MAX_CLIPS}},
    {'method': 'slice_on_vocal_change', 'arguments': {'target_clip_length_miliseconds': 3000, 'low_volume_threshold_decibels': -20.0, 'max_clips': DEFAULT_MAX_CLIPS}},
    {'method': 'slice_on_volume_change', 'arguments': {'detection_chunk_size_miliseconds': 10, 'low_volume_threshold_decibels': -20.0, 'volume_drift_decibels': 0.1, 'max_clips': DEFAULT_MAX_CLIPS}}
]

AudioProcessor(preserve_cache=True) \
    .download(tester.url(6)) \
    .metadata() \
    .normalize() \
    .slice(methods) \
    .fade() \
    .export()
