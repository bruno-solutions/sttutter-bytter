"""
The replaygain module that provides functionalities of audio leveling:
    - class ReplaygainHandler
"""

import ctypes
import pydub


TEST_DEBUG_INFO_REPLAYGAIN_C = True


class ReplaygainHandler:
    """
    The class that handles replaygain, including C/C++ portings.
    """
    def __init__(self):
        self.data_p = ctypes.c_void_p(None) # void *data = NULL;
        self.status = None
        self.is_async_locked = False
        self.audio_seg = None

        if TEST_DEBUG_INFO_REPLAYGAIN_C:
            self.generate_debug_msg()

    def generate_debug_msg(self):
        """Debugger method"""
        self.data_p = ctypes.c_char_p(
            b"replaygain.py l.29: TEST DEBUG INFO PRINT\n"
        )

    def normalize(self, audio):
        """
        The normalizer access point.
        Args:
            audio --> pydub.AudioSegment | *
        """
        self.audio_seg = audio

        # If replaygain_calc() returns REPLAYGAIN_NOT_IMPLEMENTED
        if self.smart_normalization() == -3:
            # Use peak normalization instead
            self.peak_normalization()

        return self.audio_seg

    def smart_normalization(self):
        """
        The normalization algorithm adapted from replaygain.c of MP3GAIN.
        Pending proper implementation.
        """
        assert not self.is_async_locked
        self.status = "__C_CPP_INVOKE"

        # Pending implementation
        # Convert AudioSegment object to raw bits
        # and pass C-style pointer void* buf;

        replaygain_dll = ctypes.cdll.LoadLibrary(
            'audioprocess/lib/replaygain.dll'
        )

        return replaygain_dll.replaygain_calc(self.data_p)

    def peak_normalization(self):
        """
        A less elegant method of normalization used as a substitute before
        smart_normalization() finishes implementation.
        """

        self.audio_seg = pydub.AudioSegment\
            .normalize(self.audio_seg)  # pylint: disable=no-member
