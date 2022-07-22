from typing import List

import librosa
import numpy
import pydub
from numpy import ndarray

from arguments import parse_common_arguments, to_decibels
from configuration import DEFAULT_DETECTION_WINDOW_MILISECONDS, DEFAULT_LOW_THRESHOLD, DEFAULT_DRIFT_DECIBELS
from logger import Logger
from normalizer import Normalizer
from sci import SampleClippingInterval


class VolumeSlicer:
    """
    Slice source audio recording using volume change cues
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using volume change event boundaries
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)
        low_threshold: float = to_decibels(arguments['low_threshold'], logger) if 'low_threshold' in arguments else DEFAULT_LOW_THRESHOLD
        drift: float = to_decibels(arguments['drift'], logger) if 'drift' in arguments else DEFAULT_DRIFT_DECIBELS
        chunk_size: int = arguments['detection_window'] if 'detection_window' in arguments else DEFAULT_DETECTION_WINDOW_MILISECONDS

        logger.debug(f"Slicing stage[{stage}], Volume Change Slicer: {clips} clips", separator=True)

        logger.debug(f"Downloaded Audio Segment Offset: {segment_offset_index}")
        logger.debug(f"Target Clip Length Miliseconds: {clip_size}")

        logger.debug(f"Silence Threshold Decibels: {low_threshold}")
        logger.debug(f"Per Chunk Raise Limit Decibels: {drift}")

        samples: ndarray = librosa.amplitude_to_db(Normalizer.monaural_normalization(segment))
        chunk_remainder_count: int = len(samples) % chunk_size
        padded_samples: ndarray = samples if 0 == chunk_remainder_count else numpy.pad(samples, (0, chunk_size - chunk_remainder_count))

        padded_sample_count: int = len(padded_samples)
        sample_chunk_count: int = padded_sample_count // chunk_size

        logger.debug(f"Segment Samples: {len(segment)}")
        logger.debug(f"Zero Padded Samples: {padded_sample_count}")
        logger.debug(f"Chunk Size: {chunk_size}")
        logger.debug(f"Segment Chunks: {sample_chunk_count}")

        chunk_peaks: List = []

        for chunk in padded_samples.reshape(sample_chunk_count, chunk_size):
            peak: float = low_threshold
            for sample in chunk:
                if sample > peak:
                    if sample > peak + drift:
                        peak += drift  # spiking up (attenuate the peak increase to the decibel drift factor)
                    else:
                        peak = sample  # drifting up
            chunk_peaks.append(peak)

        self.sci: List[SampleClippingInterval] = []

        clips = 0  # TODO turn peak decibels array into sample clipping intervals
        for clip_index in range(clips):
            sci = SampleClippingInterval(begin=0, end=0)
            self.sci.append(sci)
            logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
