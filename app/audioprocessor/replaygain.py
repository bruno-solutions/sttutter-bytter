"""
The module that provides audio leveling functionality:
    - class ReplayGain
"""

import ctypes
import pydub


class ReplayGain:
    """
    The class that implements ReplayGain
    """

    def __init__(self):
        self.data_p = ctypes.c_void_p(None)  # void *data = NULL;
        self.status = None
        self.is_async_locked = False
        self.audio_seg = None

    def normalize(self, audio):
        """
        The volume normalizer
        Args:
            audio --> pydub.AudioSegment | *
        """
        self.audio_seg = audio

        if self.smart_normalization() == -3:
            self.peak_normalization()  # When replaygain_calc() returns REPLAYGAIN_NOT_IMPLEMENTED

        return self.audio_seg

    def smart_normalization(self):
        """
        The normalization algorithm adapted from replaygain.c of MP3GAIN.
        Pending proper implementation.
        """
        return -3

    def peak_normalization(self):
        """
        A less elegant method of normalization used as a substitute before
        smart_normalization() finishes implementation.
        """

        self.audio_seg = pydub.AudioSegment.normalize(self.audio_seg)  # pylint: disable=no-member
