from typing import List

import librosa
import numpy
import pydub

from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval


class VolumeSlicer:
    """
    Slice source audio recording using volume change cues
    """

    def __init__(self, recording: pydub.AudioSegment, stage: int, detection_chunk_size_miliseconds: int, low_volume_threshold_decibels: int, volume_drift_decibels: int, clips: int):
        """
        Args:
        :param recording:                        an audio segment object that contains the audio samples to be processed
        :param detection_chunk_size_miliseconds: the number of samples of the recording to analyze per chunk
        :param low_volume_threshold_decibels:    the minimum decible value to use when determining the peak volume of a chunk
        :param volume_drift_decibels:            the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        :param clips:                        create no more than this many clips from the recording
        """
        self.sci: List[SampleClippingInterval] = []

        """
        Determine the peak amplitude in decibels for the chunks in an audio recording
        """
        samples = librosa.amplitude_to_db(Normalizer.monaural_normalization(recording))

        remainder = len(samples) % detection_chunk_size_miliseconds
        if 0 != remainder:
            samples = numpy.pad(samples, (0, detection_chunk_size_miliseconds - remainder))  # pad the samples to a multiple of the chunk size

        def determine_chunk_peak_decibles(chunk):
            """
            Determine the peak amplitude in decibels for the audio samples of a chunk
            Args:
                :param chunk: a portion of an audio recording
            """
            peak = low_volume_threshold_decibels

            for sample in chunk:
                if sample > peak:
                    if sample > peak + volume_drift_decibels:
                        peak += volume_drift_decibels  # spiking up (attenuate the peak increase to the decibel drift factor)
                    else:
                        peak = sample  # drifting up

            return peak

        peak_decibels = [determine_chunk_peak_decibles(chunk) for chunk in samples.reshape(len(samples) // detection_chunk_size_miliseconds, detection_chunk_size_miliseconds)]

        """
        From the peak amplitudes determine the sample clipping intervals
        """
        # TODO turn peak decibels array into sample clipping intervals self.sci.append

        if len(self.sci) >= clips:
            return

    def get(self):
        return self.sci
