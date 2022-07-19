import random
from typing import List

import pydub

from configuration import MAXIMUM_CLIP_SIZE_MILISECONDS
from logger import Logger
from sample_clipping_interval import SampleClippingInterval


class ChaosSlicer:
    """
    Random interval slicer
    """

    def __init__(self, stage: int, segment: pydub.AudioSegment, base_sample_index: int, clip_size: int, clips: int, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using a random number generator
        Args:
        :param segment:           a subset of the downloaded audio recording from which clips will be sliced
        :param base_sample_index: the index in the downloaded audio recording that corresponds to the first sample in the segment
        :param clip_size:         the number of miliseconds of the sample clipping intervals to be computed
        :param clips:             the number of sample clipping intervals to be computed for the segment
        """
        self.sci: List[SampleClippingInterval] = []

        logger.debug(f"Slicing stage[{stage}], Chaos Slicer: {clips} clips", separator=True)

        total_samples = segment.frame_count()
        sample_window = segment.frame_rate * min(clip_size, MAXIMUM_CLIP_SIZE_MILISECONDS)

        for clip_index in range(clips):
            sample_index_a = random.randint(0, total_samples)
            sample_window_left_size = min(sample_window, sample_index_a)
            sample_window_right_size = min(sample_window, total_samples - sample_index_a)
            sample_index_b = random.randint(sample_index_a - sample_window_left_size, sample_index_a + sample_window_right_size)
            sci = SampleClippingInterval(begin=base_sample_index + sample_index_a, end=base_sample_index + sample_index_b)
            self.sci.append(sci)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
