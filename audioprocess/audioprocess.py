"""The main processor of audioprocess module"""

import pydub
from pydub.utils import mediainfo

from .replaygain import ReplayGain


class AudioProcessor:
    """The class that handles overall audio processing."""

    def __init__(self, sample_rate, filename=None, load_wave_only=False):
        self.sample_rate = sample_rate
        self.base_seg = None  # pydub.AudioSegment object

        if load_wave_only:
            self.load_audio_fromwav(filename)
        else:
            raise RuntimeError("Default general file loader not implemented.")

        self.clips = list()

    def load_audio_fromwav(self, filename):
        """Loads a wave file as AudioSegmant object."""
        self.base_seg = pydub.AudioSegment.from_file(
            file=filename if filename else 'cache/ytdl-fullsong.webm'
        ).set_frame_rate(self.sample_rate)
        return self

    def preprocess(self, handler=ReplayGain):
        """Execute audio normalization."""
        self.base_seg = handler() \
            .normalize(self.base_seg)
        return self

    def apply_slicer(self, sample_rate, duration, threshold, slicer=None, count=10):
        """Loads and executes the slicer module."""
        if not slicer:
            raise RuntimeError("Default slicer loader not implemented.")
        self.clips = slicer(sample_rate, duration, threshold, self.base_seg, count)
        return self

    def postprocess(self, fadein_duration=500, fadeout_duration=500, export_path="cache"):
        """Append fade-in and fade-out."""
        for index, clip in enumerate(self.clips):
            self.clips[index] = clip \
                .fade_in(fadein_duration) \
                .fade_out(fadeout_duration)

        self.export()
        return self

    def export(self):
        """Export the sliced audio clips into the desired directory."""
        for index, clip in enumerate(self.clips):
            print(mediainfo("ytdl-fullsong.wav"))
            clip.export(f"cache/test_export/{index}.wav", tags=mediainfo("ytdl-fullsong.wav"))

        return self
