from typing import List

from .arguments import parse_common_arguments, to_milliseconds
from configuration.configuration import Configuration
from logger import Logger
from audioprocessor.normalizer import Normalizer
from .sci import SampleClippingInterval


class BeatSlicer(object):
    """
    Beat interval slicer
    """
    import pydub

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment):
        """
        Creates a list of potential clip begin and end sample indexes using "musical" beat boundaries
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        """
        import librosa
        from numpy import ndarray

        self.sci: List[SampleClippingInterval] = []

        weight, segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording)
        beats_per_clip: int = arguments['beats'] if 'beats' in arguments else Configuration().get('default_beat_count')
        attack: int = to_milliseconds(arguments['attack'], len(recording)) if 'attack' in arguments else Configuration().get('default_attack_milliseconds')
        decay: int = to_milliseconds(arguments['decay'], len(recording)) if 'decay' in arguments else Configuration().get('default_decay_milliseconds')

        sample_rate = segment.frame_rate
        attack_samples: int = (sample_rate // 1000) * attack
        decay_samples: int = (sample_rate // 1000) * decay

        maximum_clip_samples = sample_rate * (Configuration().get('maximum_clip_size_milliseconds') // 1000)
        samples = Normalizer.monaural_normalization(segment)
        total_samples: int = len(samples)

        beat_indexes: ndarray = librosa.frames_to_samples(librosa.beat.beat_track(y=samples, sr=segment.frame_rate)[1])
        beat_intervals = len(beat_indexes) - beats_per_clip

        Logger.debug(f"Slicing stage[{stage}], Beat Slicer: {clips} clips", separator=True)

        Logger.debug(f"Decay (trailing pad) Samples: {attack_samples}")
        Logger.debug(f"Attack (leading pad) Samples: {decay_samples}")

        Logger.debug(f"Requested Clipping Intervals: {clips}")
        Logger.debug(f"Found Beat Intervals: {beat_intervals}")

        Logger.debug(f"Segment Samples: {total_samples}")

        skip_count: int = 0
        beat_index: int = 0

        for clip_index in range(min(clips, len(beat_indexes) - beats_per_clip)):
            begin: int = segment_offset_index + beat_indexes[beat_index] - attack_samples
            end: int = segment_offset_index + beat_indexes[beat_index + beats_per_clip - 1] + decay_samples
            if 0 > begin or maximum_clip_samples < end - begin or total_samples < end:
                skip_count += 1
                continue
            sci = SampleClippingInterval(begin=begin, end=end)
            self.sci.append(sci)
            Logger.debug(f"Interval[{clip_index - skip_count}]: {sci.begin} {sci.end}")
            beat_index += 1

    def get(self):
        return self.sci
