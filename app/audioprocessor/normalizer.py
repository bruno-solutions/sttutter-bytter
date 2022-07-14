"""
The module that provides audio volume leveling functionality:
    - class Normalizer
"""
import numpy
import pydub


class Normalizer:
    """
    The class that implements ReplayGain
    """
    pydub = getattr(pydub.AudioSegment, 'normalize')

    def __init__(self, normalizer=pydub):
        self.normalizer = normalizer

    def normalize(self, segment, normalizer=None):
        """
        The volume normalizer
        Args:
            segment --> pydub.AudioSegment | *
        """
        return normalizer(segment) if normalizer is not None else self.normalizer(segment)

    @staticmethod
    def monaural_normalization(samples, sample_width):
        """
        Converts the track values into librosa-compatible format
        int16 or int32 values to float values between -1. and 1.
        """
        stereo = numpy.array(samples)
        left_channel = stereo[::2]
        right_channel = stereo[1::2]
        monaural = (left_channel + right_channel) / 2

        # Convert int16 or int32 data to float (-1. ~ 1.)
        return monaural / (1 << (sample_width * 8) - 1)
