from typing import List

import librosa
import pydub
from numpy import ndarray

from arguments import parse_common_arguments
from logger import Logger
from sci import SampleClippingInterval


class OnsetSlicer:
    """
    Onset slicer
    Locates note onset events by picking peaks in an onset strength envelope to define sample clipping intervals
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using (major sound change) onset detection
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)

        total_samples: int = int(segment.frame_count())

        logger.debug(f"Slicing stage[{stage}], Onset Detection Slicer: {clips} clips", separator=True)

        logger.debug(f"Segment Samples: {total_samples}")

        self.sci: List[SampleClippingInterval] = []

        # https://librosa.org/doc/main/generated/librosa.to_mono.html
        # https://librosa.org/doc/main/generated/librosa.onset.onset_detect.html

        onsets: ndarray = librosa.onset.onset_detect(y=librosa.to_mono(y=recording.get_array_of_samples()), sr=recording.frame_rate)

        clips = 0  # TODO turn the onset array into sample clipping intervals
        for clip_index in range(clips):
            sci = SampleClippingInterval(begin=0, end=0)
            self.sci.append(sci)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
