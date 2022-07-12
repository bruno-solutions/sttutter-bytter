"""
The main audio processing module
"""
import json
from pathlib import Path

import pydub

import downloader
from configuration import EXTERNAL_DOWNLOADER, DOWNLOADED_AUDIO_FILE_NAME, EXPORT_FILE_TYPE, DURATION, THRESHOLD, CLIP_LIMIT, DEFAULT_SAMPLE_RATE, METADATA_FILE_NAME
from replaygain import ReplayGain
from slicer import Slicer
from tagger import Tagger


class AudioProcessor:
    """
    The class that orchestrates the audio processing methods
    """

    def __init__(self, url, slicer_name, slicer_method, downloaded_audio_file_name=DOWNLOADED_AUDIO_FILE_NAME, sample_rate=DEFAULT_SAMPLE_RATE, external_downloader=EXTERNAL_DOWNLOADER, logger=None):
        self.url = url

        self.downloaded_audio_file_name = downloaded_audio_file_name
        self.sample_rate = sample_rate
        self.slicer_name = slicer_name

        self.external_downloader = external_downloader
        self.logger = logger
        self.recording = None
        self.tagger = None

        Slicer.register({slicer_name: slicer_method}, self.tagger)

        self.clips = list()

    def download(self):
        """
        Downloads a file and converts it into a pydub AudioSegmant object
        """
        downloader.download(self.url, logger=self.logger, external_downloader=self.external_downloader)
        self.recording = pydub.AudioSegment.from_file(self.downloaded_audio_file_name).set_frame_rate(self.sample_rate)
        return self

    def metadata(self):
        with open(METADATA_FILE_NAME) as json_file:
            self.tagger = Tagger(json.load(json_file))
            self.tagger.write_tags(self.downloaded_audio_file_name)
        return self

    def normalize(self, handler=ReplayGain):
        """
        Execute audio normalization
        """
        self.recording = handler().normalize(self.recording)
        return self

    def slice(self, duration=DURATION, threshold=THRESHOLD, clip_limit=CLIP_LIMIT):
        """
        Loads and executes the slicer module
        """
        slicer = getattr(pydub.AudioSegment, self.slicer_name)

        if not slicer:
            raise RuntimeError("Slicer not configured")

        self.clips = slicer(self.sample_rate, duration, threshold, self.recording, clip_limit)
        return self

    def fade(self, fadein_duration=500, fadeout_duration=500):
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
            clip.export(filename, format=EXPORT_FILE_TYPE).close()
            self.tagger.write_tags(filename)
        return self
