from typing import List

import pydub

from arguments import parse_common_arguments
from configuration import MAXIMUM_CLIP_SIZE_MILISECONDS
from logger import Logger
from sample_clipping_interval import SampleClippingInterval


class SimpleIntervalSlicer:
    """
    A simple time interval slicer
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes based upon time intervals
        Note: dependent upon the length of the recording segment, the length of the clips, and the number of clips
              clips can be taken overlapping or separated by gaps from the downloaded audio recording
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, base_sample_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)

        logger.debug(f"Slicing stage[{stage}], Interval Slicer: {clips} clips", separator=True)

        total_samples: int = int(segment.frame_count())
        samples_per_clip: int = int(recording.frame_rate * (min(clip_size, MAXIMUM_CLIP_SIZE_MILISECONDS) / 1000))
        max_possible_clips: int = total_samples // samples_per_clip

        cumulative_samples_to_skip = total_samples - (clips * samples_per_clip)
        skips = clips - 1
        samples_per_skip = cumulative_samples_to_skip // skips

        samples_per_iteration = samples_per_clip + samples_per_skip

        logger.debug(f"Maximum Possible Clips: {max_possible_clips}")

        logger.debug(f"Samples per Clip: {samples_per_clip}")
        logger.debug(f"Clipping Intervals: {clips}")
        logger.debug(f"Cumulative Samples to be Clipped: {clips * samples_per_clip}")

        logger.debug(f"Samples per Skip: {samples_per_skip}")
        logger.debug(f"Skipping Intervals: {skips}")
        logger.debug(f"Cumulative Samples to be Skipped: {cumulative_samples_to_skip}")

        logger.debug(f"Clip + Skip Samples: {samples_per_iteration}")
        logger.debug(f"Clips + Skips Samples: {clips * samples_per_clip + skips * samples_per_skip}")
        logger.debug(f"Segment Samples: {total_samples}")

        self.sci: List[SampleClippingInterval] = []

        sample_index = base_sample_index

        for clip_index in range(clips):
            end_index = sample_index + samples_per_clip
            if total_samples < end_index:
                logger.warning(f"The sample index {sample_index} tried to pass the end of the recording at {total_samples} samples")
                break
            sci = SampleClippingInterval(begin=sample_index, end=end_index)
            self.sci.append(sci)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")
            sample_index += samples_per_iteration

    def get(self):
        return self.sci
