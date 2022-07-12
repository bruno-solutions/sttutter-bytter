import librosa
import numpy

from configuration import DEFAULT_SAMPLE_RATE


class VolumeSlicer:
    """
    Volume change slicer
    """

    def __init__(self, recording, chunk_size=DEFAULT_SAMPLE_RATE // 100, base=-20.0, drift=0.1):
        """
        Args:
            :param recording:  the audio samples of the recording
            :param chunk_size: the number of audio samples of the recording to analyze per chunk
            :param base:       the minimum decible value to use when determining the peak volume of a chunk
            :param drift:      the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        """

        def determine_peak_decibels():
            """
            Determine the peak amplitude in decibels for the chunks of a collection of audio samples
            """

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

            samples = librosa.amplitude_to_db(recording)
            remainder = len(samples) % chunk_size
            if 0 != remainder:
                samples = numpy.pad(samples, (0, chunk_size - remainder))
            return [determine_chunk_peak_decibles(chunk) for chunk in samples.reshape(len(samples) // chunk_size, chunk_size)]

        self.peak_decibels = determine_peak_decibels()

    def write_critical_time(self, cti):
        """
        Write volume change information to the Critical Time Index
        """
        # TODO check/fix: the following is a wild guess as to the original intent (if it ever actually worked)
        for peak_volume in self.peak_decibels:
            cti.append(cti=peak_volume)
