from typing import List

import librosa
import pydub
from numpy import ndarray

from arguments import parse_common_arguments
from logger import Logger
from sci import SampleClippingInterval


class TempoSlicer(object):
    """
    Tempo change slicer
    Locates tempo (beats per minute) change events to define sample clipping intervals
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using tempo (beats per minute) change detection
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)

        total_samples: int = int(segment.frame_count())

        logger.debug(f"Slicing stage[{stage}], Tempo Change Slicer: {clips} clips", separator=True)

        logger.debug(f"Segment Samples: {total_samples}")

        self.sci: List[SampleClippingInterval] = []

        # https://librosa.org/doc/main/generated/librosa.to_mono.html
        # https://librosa.org/doc/main/generated/librosa.onset.onset_strength.html
        # https://librosa.org/doc/main/generated/librosa.beat.tempo.html

        onset_env = librosa.onset.onset_strength(y=librosa.to_mono(y=recording.get_array_of_samples()), sr=recording.frame_rate)
        changes: ndarray = librosa.beat.tempo(onset_envelope=onset_env, sr=recording.frame_rate, aggregate=None)

        clips = 0  # TODO turn the tempo change points array into sample clipping intervals
        for clip_index in range(clips):

            # difference: float = math.fabs(changes[1] - changes[0])
            # for index in range(changes.size - 1):
            #     if difference + 2 < math.fabs(changes[index + 1] - changes[index]):
            #         difference = math.fabs(changes[index + 1] - changes[index])
            # if difference == math.fabs(changes[1] - changes[0]):
            #     return

            sci = SampleClippingInterval(begin=0, end=0)
            self.sci.append(sci)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
