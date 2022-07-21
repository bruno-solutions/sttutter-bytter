from typing import List

import librosa
import pydub
from numpy import ndarray

from arguments import parse_common_arguments, to_miliseconds
from configuration import DEFAULT_BEAT_COUNT, DEFAULT_ATTACK_MILISECONDS, DEFAULT_DECAY_MILISECONDS, MAXIMUM_CLIP_SIZE_MILISECONDS
from logger import Logger
from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval


class BeatSlicer:
    """
    Beat interval slicer
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using "musical" beat boundaries
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)
        beats_per_clip: int = arguments['beats'] if 'beats' in arguments else DEFAULT_BEAT_COUNT
        attack: int = to_miliseconds(arguments['attack'], len(recording), logger) if 'attack' in arguments else DEFAULT_ATTACK_MILISECONDS
        decay: int = to_miliseconds(arguments['decay'], len(recording), logger) if 'decay' in arguments else DEFAULT_DECAY_MILISECONDS

        sample_rate = segment.frame_rate
        attack_samples: int = (sample_rate // 1000) * attack
        decay_samples: int = (sample_rate // 1000) * decay

        maximum_clip_samples = sample_rate * (MAXIMUM_CLIP_SIZE_MILISECONDS // 1000)
        samples = Normalizer.monaural_normalization(segment)
        total_samples: int = len(samples)

        beat_indexes: ndarray = librosa.frames_to_samples(librosa.beat.beat_track(y=samples, sr=segment.frame_rate)[1])
        beat_intervals = len(beat_indexes) - beats_per_clip

        logger.debug(f"Slicing stage[{stage}], Beat Slicer: {clips} clips", separator=True)

        logger.debug(f"Decay (trailing pad) Samples: {attack_samples}")
        logger.debug(f"Attack (leading pad) Samples: {decay_samples}")

        logger.debug(f"Requested Clipping Intervals: {clips}")
        logger.debug(f"Found Beat Intervals: {beat_intervals}")

        logger.debug(f"Segment Samples: {total_samples}")

        self.sci: List[SampleClippingInterval] = []

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
            logger.debug(f"Interval[{clip_index - skip_count}]: {sci.begin} {sci.end}")
            beat_index += 1

    def get(self):
        return self.sci
