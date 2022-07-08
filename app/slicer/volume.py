import librosa
import numpy

from configuration import DEFAULT_SAMPLE_RATE


class VolumeSlicer:
    """
    Volume change slicer
    """

    def __init__(self, samples, chunk_size=DEFAULT_SAMPLE_RATE / 1000, base=-20.0, drift=0.1):
        self.peak_decibels = self.determine_peak_decibels(samples, chunk_size, base, drift)

    def determine_peak_decibels(self, recording, chunk_size=DEFAULT_SAMPLE_RATE / 1000, base=-20.0, drift=0.1):
        """
        Determine the peak amplitude in decibels for the chunks of a collection of audio samples
        Args:
            :param recording:  the audio samples of an audio recording
            :param chunk_size: the number of samples of the audio recording to analyze as a chunk
            :param base:       the minimum decible value to use when determining the peak volume of a chunk
            :param drift:      the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        """
        return [
            self.determine_chunk_peak_decibles(chunk, base, drift)
            for chunk in numpy.pad(librosa.amplitude_to_db(recording), (0, len(recording) % chunk_size)).reshape((len(recording) - 1) // chunk_size + 1, chunk_size)
        ]

    @staticmethod
    def determine_chunk_peak_decibles(chunk, base=-20.0, drift=0.1):
        """
        Determine the peak amplitude in decibels for an audio sample chunk
        Args:
            :param chunk: a portion of an audio recording
            :param base:  the minimum decible value to use when determining the peak volume of a chunk
            :param drift: the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        """
        peak = base
        for sample in chunk:
            if sample > peak:
                if sample > peak + drift:
                    peak += drift  # spiking up (attenuate the peak increase to the decibel drift factor)
                else:
                    peak = sample  # drifting up
        return peak

    def write_critical_time(self, cti):
        """
        Write volume change information to the Critical Time Index
        """
        # TODO check/fix: the following is a wild guess as to the original intent (if it ever actually worked)
        for peak_volume in self.peak_decibels:
            cti.append(cti=peak_volume)
