from typing import List

import librosa
import numpy
import pydub
from numpy import ndarray

from arguments import parse_common_arguments, to_decibels
from configuration.configuration import Configuration
from logger import Logger
from normalizer import Normalizer
from sci import SampleClippingInterval


class VolumeSlicer(object):
    """
    Slice source audio recording using volume change cues
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment) -> None:
        """
        Creates a list of potential clip begin and end sample indexes using volume change event boundaries
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        """
        self.sci: List[SampleClippingInterval] = []

        active, weight, segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording)

        if not active or 0 == weight:
            return

        low_threshold: float = to_decibels(arguments['low_threshold']) if 'low_threshold' in arguments else Configuration().get('low_threshold')
        drift: float = to_decibels(arguments['drift']) if 'drift' in arguments else Configuration().get('drift_decibels')
        chunk_size: int = arguments['detection_window'] if 'detection_window' in arguments else Configuration().get('detection_window_miliseconds')

        Logger.debug(f"Slicing stage[{stage}], Volume Change Slicer: {clips} clips", separator=True)

        Logger.debug(f"Downloaded Audio Segment Offset: {segment_offset_index}")
        Logger.debug(f"Target Clip Length Miliseconds: {clip_size}")

        Logger.debug(f"Silence Threshold Decibels: {low_threshold}")
        Logger.debug(f"Per Chunk Raise Limit Decibels: {drift}")

        samples: ndarray = librosa.amplitude_to_db(Normalizer.monaural_normalization(segment))
        chunk_remainder_count: int = len(samples) % chunk_size
        padded_samples: ndarray = samples if 0 == chunk_remainder_count else numpy.pad(samples, (0, chunk_size - chunk_remainder_count))

        padded_sample_count: int = len(padded_samples)
        sample_chunk_count: int = padded_sample_count // chunk_size

        Logger.debug(f"Segment Samples: {len(segment)}")
        Logger.debug(f"Zero Padded Samples: {padded_sample_count}")
        Logger.debug(f"Chunk Size: {chunk_size}")
        Logger.debug(f"Segment Chunks: {sample_chunk_count}")

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

        clips = 0  # TODO turn peak decibels array into sample clipping intervals
        for clip_index in range(clips):
            sci = SampleClippingInterval(begin=0, end=0)
            self.sci.append(sci)
            Logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
