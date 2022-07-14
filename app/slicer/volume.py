from typing import List

import librosa
import numpy
import pydub

from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval


class VolumeSlicer:
    """
    Volume change slicer
    """

    def __init__(self, recording: pydub.AudioSegment, chunk_size, base=-20.0, drift=0.1):
        """
        Args:
        :param recording:  an audio segment object that contains the audio samples to be processed
        :param chunk_size: the number of samples of the recording to analyze per chunk
        :param base:       the minimum decible value to use when determining the peak volume of a chunk
        :param drift:      the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        """
        self.sci: List[SampleClippingInterval] = []

        """
        Determine the peak amplitude in decibels for the chunks in an audio recording
        """
        samples = librosa.amplitude_to_db(Normalizer.monaural_normalization(recording.get_array_of_samples(), recording.sample_width))

        def determine_chunk_peak_decibles(chunk):
            """
            Determine the peak amplitude in decibels for the audio samples of a chunk
            Args:
                :param chunk: a portion of an audio recording
            """
            peak = base

            for sample in chunk:
                if sample > peak:
                    if sample > peak + drift:
                        peak += drift  # spiking up (attenuate the peak increase to the decibel drift factor)
                    else:
                        peak = sample  # drifting up

            return peak

        remainder = len(samples) % chunk_size
        if 0 != remainder:
            samples = numpy.pad(samples, (0, chunk_size - remainder))  # pad the samples to a multiple of the chunk size

        peak_decibels = [determine_chunk_peak_decibles(chunk) for chunk in samples.reshape(len(samples) // chunk_size, chunk_size)]

        """
        From the peak amplitudes determine the sample clipping intervals
        """
        # TODO turn peak decibels array into sample clipping intervals self.sci.append()

    def get(self):
        return self.sci
