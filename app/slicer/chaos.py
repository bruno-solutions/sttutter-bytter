import random
from typing import List

import pydub

from arguments import parse_common_arguments
from configuration import MAXIMUM_CLIP_SIZE_MILISECONDS
from logger import Logger
from sample_clipping_interval import SampleClippingInterval


class ChaosSlicer:
    """
    Random interval slicer
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using a random number generator
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)

        logger.debug(f"Slicing stage[{stage}], Chaos Slicer: {clips} clips", separator=True)

        total_samples: int = int(segment.frame_count())
        sample_window: int = segment.frame_rate * min(clip_size, MAXIMUM_CLIP_SIZE_MILISECONDS)

        logger.debug(f"Segment Sample Window: {sample_window}")
        logger.debug(f"Segment Samples: {total_samples}")

        self.sci: List[SampleClippingInterval] = []

        for clip_index in range(clips):
            sample_index_a = random.randint(0, total_samples)
            sample_window_left_size = min(sample_window, sample_index_a)
            sample_window_right_size = min(sample_window, total_samples - sample_index_a)
            sample_index_b = random.randint(sample_index_a - sample_window_left_size, sample_index_a + sample_window_right_size)
            sci = SampleClippingInterval(begin=segment_offset_index + sample_index_a, end=segment_offset_index + sample_index_b)
            self.sci.append(sci)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
