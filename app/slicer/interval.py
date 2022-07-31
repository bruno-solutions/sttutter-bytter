from typing import List

import pydub

from arguments import parse_common_arguments
from configuration.configuration import Configuration
from logger import Logger
from sci import SampleClippingInterval


class SimpleIntervalSlicer(object):
    """
    A simple time interval slicer
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment) -> None:
        """
        Creates a list of potential clip begin and end sample indexes based upon time intervals
        Note: dependent upon the length of the recording segment, the length of the clips, and the number of clips
              clips can be taken overlapping or separated by gaps from the downloaded audio recording
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        """
        self.sci: List[SampleClippingInterval] = []

        weight, segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording)

        total_samples: int = int(segment.frame_count())
        samples_per_clip: int = int(segment.frame_rate * (min(clip_size, Configuration().get('maximum_clip_size_miliseconds')) / 1000))
        max_possible_clips: int = total_samples // samples_per_clip

        cumulative_samples_to_skip = total_samples - (clips * samples_per_clip)
        skips = clips - 1
        samples_per_skip = cumulative_samples_to_skip // skips

        samples_per_iteration = samples_per_clip + samples_per_skip

        Logger.debug(f"Slicing stage[{stage}], Interval Slicer: {clips} clips", separator=True)

        Logger.debug(f"Maximum Possible Clips: {max_possible_clips}")

        Logger.debug(f"Samples per Clip: {samples_per_clip}")
        Logger.debug(f"Requested Clipping Intervals: {clips}")
        Logger.debug(f"Cumulative Samples to be Clipped: {clips * samples_per_clip}")

        Logger.debug(f"Samples per Skip: {samples_per_skip}")
        Logger.debug(f"Calculated Skipping Intervals: {skips}")
        Logger.debug(f"Cumulative Samples to be Skipped: {cumulative_samples_to_skip}")

        Logger.debug(f"Clip + Skip Samples: {samples_per_iteration}")
        Logger.debug(f"Clips + Skips Samples: {clips * samples_per_clip + skips * samples_per_skip}")
        Logger.debug(f"Segment Samples: {total_samples}")

        begin_index = segment_offset_index

        for clip_index in range(clips):
            end_index = begin_index + samples_per_clip
            if total_samples < end_index:
                Logger.warning(f"The sample index {end_index} tried to pass the end of the recording at {total_samples} samples")
                break
            sci = SampleClippingInterval(begin=begin_index, end=end_index)
            self.sci += weight * [sci]
            Logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")
            begin_index += samples_per_iteration

    def get(self):
        return self.sci
