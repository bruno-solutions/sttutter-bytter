"""
The main audio processing module
"""

import pydub

from configuration import EXPORT_ROOT, EXPORT_FILE_TYPE
from tags import write_tags
from .replaygain import ReplayGain


class AudioProcessor:
    """
    The class that handles overall audio processing
    """

    def __init__(self, filename, sample_rate):
        self.source_audio_segment = None
        self.sliced_audio_segments = list()

        self.load_audio_segment(filename, sample_rate)

    def load_audio_segment(self, filename, sample_rate):
        """
        Loads a file as a pydub AudioSegmant object
        """

        self.source_audio_segment = pydub.AudioSegment.from_file(filename).set_frame_rate(sample_rate)
        return self

    def preprocess(self, handler=ReplayGain):
        """
        Execute audio normalization
        """

        self.source_audio_segment = handler().normalize(self.source_audio_segment)
        return self

    def apply_slicer(self, sample_rate, duration, threshold, slicer=None, count=10):
        """
        Loads and executes the slicer module
        """

        if not slicer:
            raise RuntimeError("Default slicer loader not implemented.")

        self.sliced_audio_segments = slicer(sample_rate, duration, threshold, self.source_audio_segment, count)
        return self

    def postprocess(self, tags, fadein_duration=500, fadeout_duration=500, export_root=EXPORT_ROOT):
        """
        Append fade-in and fade-out
        """

        for index, clip in enumerate(self.sliced_audio_segments):
            self.sliced_audio_segments[index] = clip.fade_in(fadein_duration).fade_out(fadeout_duration)

        self.export(tags, export_root)
        return self

    def export(self, tags, export_root):
        """
        Export the sliced audio clips into the desired directory
        """

        for index, clip in enumerate(self.sliced_audio_segments):
            filename = f"{export_root}/{index}.{EXPORT_FILE_TYPE}"
            clip.export(filename, format=EXPORT_FILE_TYPE)
            write_tags(filename, tags)

        return self
