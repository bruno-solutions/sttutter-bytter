"""The main processor of audioprocess module"""

import pydub

from audioprocess.replaygain import ReplaygainHandler


DEBUG_DEF_LOAD_WAV_ONLY = True


class AudioProcessor:
    """The class that handles overall audio processing."""
    def __init__(self, filename=None):
        self.base_seg = None # pydub.AudioSegment object

        if DEBUG_DEF_LOAD_WAV_ONLY:
            self.load_audio_fromwav(filename)
        else:
            raise RuntimeError("Default general file loader not implemented.")

        self.clips = list()

    def load_audio_fromwav(self, filename):
        """Loads a wave file as AudioSegmant object."""
        self.base_seg = pydub.AudioSegment.from_file(
            file=filename if filename else 'cache/ytdl-fullsong.webm'
        )
        return self

    def preprocess(self, handler=ReplaygainHandler):
        """Execute audio normalization."""
        self.base_seg = handler()\
            .normalize(self.base_seg)
        return self

    def apply_slicer(self, slicer=None, count=10):
        """Loads and executes the slicer module."""
        if not slicer:
            raise RuntimeError("Default slicer loader not implemented.")
        self.clips = slicer(self.base_seg, count)
        return self

    def postprocess(self, fadein_duration=500, fadeout_duration=500, export_path="cache"):
        """Append fade-in and fade-out."""
        for index, clip in enumerate(self.clips):
            self.clips[index] = clip\
                .fade_in(fadein_duration)\
                .fade_out(fadeout_duration)

        self.export()
        return self

    def export(self):
        """DOCSTRING"""
        for index, clip in enumerate(self.clips):
            clip.export(f"cache/test_export/{index}.wav")

        return self
