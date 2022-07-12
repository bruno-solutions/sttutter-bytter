"""
The main audio processing module
"""
from pathlib import Path

import pydub

import downloader
from configuration import EXPORT_FILE_TYPE
from replaygain import ReplayGain
from slicer import Slicer


class AudioProcessor:
    """
    The class that handles overall audio processing
    """

    def __init__(self, url, filename, sample_rate, slicer_name, slicer_method):
        self.tagger = downloader.get_song_aria2c(url)

        self.sample_rate = sample_rate
        self.recording = None
        self.clips = list()
        self.load(filename)
        self.slicer_name = slicer_name

        Slicer.register({slicer_name: slicer_method}, self.tagger)

    def load(self, filename):
        """
        Loads a file as a pydub AudioSegmant object
        """
        self.recording = pydub.AudioSegment.from_file(filename).set_frame_rate(self.sample_rate)
        return self

    def preprocess(self, handler=ReplayGain):
        """
        Execute audio normalization
        """
        self.recording = handler().normalize(self.recording)
        return self

    def slice(self, duration, threshold, count=10):
        """
        Loads and executes the slicer module
        """
        slicer = getattr(pydub.AudioSegment, self.slicer_name)

        if not slicer:
            raise RuntimeError("Slicer not configured")

        self.clips = slicer(self.sample_rate, duration, threshold, self.recording, count)
        return self

    def postprocess(self, fadein_duration=500, fadeout_duration=500):
        """
        Append fade-in and fade-out
        """
        for index, clip in enumerate(self.clips):
            self.clips[index] = clip.fade_in(fadein_duration).fade_out(fadeout_duration)
        return self

    def export(self, directory):
        """
        Export the sliced audio clips into the desired directory
        """
        for index, clip in enumerate(self.clips):
            Path(directory).mkdir(parents=True, exist_ok=True)
            filename = f"{directory}\\{index}.{EXPORT_FILE_TYPE}"
            file_object = clip.export(filename, format=EXPORT_FILE_TYPE)
            file_object.close()
            self.tagger.write_tags(filename)
        return self
