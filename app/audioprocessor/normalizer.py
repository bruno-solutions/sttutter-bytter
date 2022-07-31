"""
The module that provides audio volume leveling functionality
"""


class Normalizer(object):
    """
    The class that implements ReplayGain
    """
    import pydub

    stereo_normalizer = getattr(pydub.AudioSegment, 'normalize')

    @staticmethod
    def stereo_normalization(recording: pydub.AudioSegment) -> pydub.AudioSegment:
        """
        Stereo volume normalization
        Args:
        :param recording: an audio segment object that contains the audio samples to be processed
        """
        return Normalizer.stereo_normalizer(recording)

    from numpy import ndarray

    @staticmethod
    def monaural_normalization(recording: pydub.AudioSegment) -> ndarray:
        """
        Stereo to monaural volume normalization
        Args:
        :param recording: an audio segment object that contains the audio samples to be processed
        """
        import numpy
        from numpy import ndarray

        stereo: ndarray = numpy.array(recording.get_array_of_samples())
        left_channel: ndarray = stereo[::2]
        right_channel: ndarray = stereo[1::2]
        monaural: ndarray = (left_channel + right_channel) / 2

        # Scale sample (int16 or int32) values to librosa-compatible (float) values between -1.0 and 1.0
        return monaural / (1 << (recording.sample_width * 8) - 1)
