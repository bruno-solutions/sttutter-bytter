"""
The module that provides audio volume leveling functionality
"""
import numpy
import pydub


class Normalizer:
    """
    The class that implements ReplayGain
    """
    stereo_normalizer = getattr(pydub.AudioSegment, 'normalize')

    @staticmethod
    def stereo_normalization(recording: pydub.AudioSegment):
        """
        Stereo volume normalization
        Args:
        :param recording: an audio segment object that contains the audio samples to be processed
        """
        return Normalizer.stereo_normalizer(recording)

    @staticmethod
    def monaural_normalization(recording: pydub.AudioSegment):
        """
        Stereo to monaural volume normalization
        Args:
        :param recording: an audio segment object that contains the audio samples to be processed
        """
        # TODO: Does "channels = recording.split_to_mono()" makes more sense to split the channels?
        stereo = numpy.array(recording.get_array_of_samples())
        left_channel = stereo[::2]
        right_channel = stereo[1::2]
        monaural = (left_channel + right_channel) / 2

        # Scale sample (int16 or int32) values to librosa-compatible (float) values between -1.0 and 1.0
        return monaural / (1 << (recording.sample_width * 8) - 1)
