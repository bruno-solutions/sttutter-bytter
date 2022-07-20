"""The main module"""

import tester
from audioprocessor import AudioProcessor

# TODO [Enhancement] enable method combining (combine/compare the nearness sample clipping intervals to evaluate the quality of a clip)
# TODO [Enhancement] enable method chaining (feed samples from one method into another to create sub-clips)

methods: [{}] = [
    {'method': 'slice_on_beat', 'arguments': {'begin': 0, 'end': 1, 'beats': 4, 'attack': '25ms', 'decay': 75, 'clips': 15}},
    {'method': 'slice_at_interval', 'arguments': {'begin': 0, 'end': 1, 'clip_size': '7500 ms', 'clips': 7}},
    {'method': 'slice_at_random'},
    {'method': 'slice_at_random', 'arguments': {'clips': 2}},
    {'method': 'slice_at_random', 'arguments': {'clip_size': '9000 ms', 'clips': 3}},
    {'method': 'slice_at_random', 'arguments': {'begin': '2 seconds', 'clip_size': '9000 ms', 'clips': 4}},
    {'method': 'slice_at_random', 'arguments': {'begin': '1111ms', 'end': '88%', 'clip_size': '15500 ms', 'clips': 5}},
    # {'method': 'slice_on_vocal_change', 'arguments': {'begin': 0, 'end': 1, 'passes': 1, 'model': 'spleeter:5stems-16kHz', 'detection_window': 20, 'low_threshold': -20.0, 'drift': 0.1, 'clips': 20}},
    # {'method': 'slice_on_volume_change', 'arguments': {'begin': 0, 'end': 1, 'detection_window': 10, 'low_threshold': -20.0, 'drift': 0.1}},
    # {'method': 'slice_at_random', 'arguments': {'begin': 0, 'end': 1, 'pad_miliseconds': 250}}
]

AudioProcessor(preserve_cache=True) \
    .download(tester.source(1)) \
    .normalize() \
    .slice(methods) \
    .fade() \
    .export()
