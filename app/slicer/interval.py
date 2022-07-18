from typing import List

import pydub

from logger import Logger
from sample_clipping_interval import SampleClippingInterval


class SimpleIntervalSlicer:
    """
    A simple time interval slicer
    """

    def __init__(self, recording: pydub.AudioSegment, stage: int, duration: int, max_clips: int, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes based upon time interval calculations
        Args:
        :param recording: an audio segment object that contains the audio samples to be processed
        :param duration:  the number of miliseconds per clipping interval
        :param max_clips: create no more than this many clips from the recording
        """
        self.sci: List[SampleClippingInterval] = []

        logger.debug(f"Slicing stage[{stage}], Interval Slicer {duration} miliseconds per clip", separator=True)

        recording_samples: int = recording.frame_rate * (len(recording) // 1000)
        samples_per_clip: int = recording.frame_rate * (duration // 1000)
        max_possible_clips: int = recording_samples // samples_per_clip

        cumulative_samples_to_skip = recording_samples - (max_clips * samples_per_clip)
        skips = max_clips - 1
        samples_per_skip = cumulative_samples_to_skip // skips

        samples_per_iteration = samples_per_clip + samples_per_skip

        logger.debug(f"Maximum Possible Clips: {max_possible_clips}")

        logger.debug(f"Samples per Clip: {samples_per_clip}")
        logger.debug(f"Clipping Intervals: {max_clips}")
        logger.debug(f"Cumulative Samples to be Clipped: {max_clips * samples_per_clip}")

        logger.debug(f"Samples per Skip: {samples_per_skip}")
        logger.debug(f"Skipping Intervals: {skips}")
        logger.debug(f"Cumulative Samples to be Skipped: {cumulative_samples_to_skip}")

        logger.debug(f"Clip + Skip Samples: {samples_per_iteration}")
        logger.debug(f"Clips + Skips Samples: {max_clips * samples_per_clip + skips * samples_per_skip}")
        logger.debug(f"Recording Samples: {recording_samples}")

        clip_index = sample_index = 0

        while max_clips > clip_index:
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
