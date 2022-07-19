from typing import List

import pydub

from logger import Logger
from sample_clipping_interval import SampleClippingInterval


class SimpleIntervalSlicer:
    """
    A simple time interval slicer
    """

    def __init__(self, segment: pydub.AudioSegment, stage: int, base_sample_index: int, clip_size_ms: int, clips: int, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes based upon time interval calculations
        Args:
        :param segment:           a subset of the downloaded audio recording from which clips will be sliced
        :param base_sample_index: the index in the downloaded audio recording that corresponds to the first sample in the segment
        :param clip_size_ms:      the number of miliseconds of the sample clipping intervals to be computed
        :param clips:             the number of sample clipping intervals to be computed for the segment
        """
        self.sci: List[SampleClippingInterval] = []

        logger.debug(f"Slicing stage[{stage}], Interval Slicer {clip_size_ms} miliseconds per clip", separator=True)

        recording_samples: int = segment.frame_rate * (len(segment) // 1000)
        samples_per_clip: int = segment.frame_rate * (clip_size_ms // 1000)
        max_possible_clips: int = recording_samples // samples_per_clip

        cumulative_samples_to_skip = recording_samples - (clips * samples_per_clip)
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
        logger.debug(f"Recording Samples: {recording_samples}")

        clip_index = 0
        sample_index = base_sample_index
        while clips > clip_index:
            clip_index += 1
            end_index = sample_index + samples_per_clip
            if recording_samples < end_index:
                logger.warning(f"The sample index {sample_index} tried to pass the end of the recording at {recording_samples} samples")
                break
            sci = SampleClippingInterval(begin=sample_index, end=end_index)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")
            self.sci.append(sci)
            sample_index += samples_per_iteration

    def get(self):
        return self.sci
