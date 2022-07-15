"""
The main audio processing module
"""
import hashlib
import json
from pathlib import Path

import pydub

import downloader
import file
from configuration import DEFAULT_EXTERNAL_DOWNLOADER, AUDIO_FILE_TYPE, DEFAULT_SAMPLE_RATE, CACHE_ROOT, METADATA_FILE_TYPE, DEFAULT_FADE_IN_MILISECONDS, DEFAULT_FADE_OUT_MILISECONDS, EXPORT_ROOT
from logger import Logger
from normalizer import Normalizer
from slicer import Slicer
from tagger import Tagger


class AudioProcessor:
    """
    The class that orchestrates the audio processing methods
    """

    def __init__(self, sample_rate=DEFAULT_SAMPLE_RATE, external_downloader=DEFAULT_EXTERNAL_DOWNLOADER, logger=Logger(), preserve_cache=True):
        """
        Use specified URL to download a song from the internet and save it as a file
        Args:
        :param sample_rate:         The audio samples per second to make the extracted audio file | None to use the default sample rate
        :param external_downloader: A library for YouTube Download to use for file download | None to use the built-in downloader
        :param logger:              User supplied logger class | None to use the built-in Logger
        :param preserve_cache:      Should downloaded source media files be kept after processing to prevent re-download later
        """
        self.url = None
        self.download_file_name = None
        self.audio_file_name = None
        self.metadata_file_name = None

        self.sample_rate = sample_rate

        self.external_downloader = external_downloader
        self.logger = logger
        self.recording = None
        self.tagger = None
        self.slicer = None

        self.clips = list()

        if preserve_cache:
            file.cleanup(cache_root=None)
        else:
            file.cleanup()

    def download(self, url):
        """
        Downloads a file and converts it into a pydub AudioSegmant object
        Args:
        :param url: The source URL from which to extract audio
        """
        self.url = url
        self.download_file_name = f"{CACHE_ROOT}\\{hashlib.md5(url.encode('utf-8')).hexdigest().upper()}"
        self.audio_file_name = f"{self.download_file_name}.{AUDIO_FILE_TYPE}"
        self.metadata_file_name = f"{self.download_file_name}.{METADATA_FILE_TYPE}"

        self.logger.debug(f"Target sample rate: {self.sample_rate}")
        downloader.download(self.url, directory=CACHE_ROOT, filename=self.download_file_name, logger=self.logger, external_downloader=self.external_downloader)
        self.recording = pydub.AudioSegment.from_file(self.audio_file_name)
        self.recording = self.recording.set_frame_rate(self.sample_rate)
        self.recording.frame_count()
        self.logger.characteristics(self.recording)
        return self

    def metadata(self):
        with open(self.metadata_file_name) as json_file:
            self.tagger = Tagger(json.load(json_file))
            self.tagger.write_tags(self.audio_file_name)
        return self

    def normalize(self):
        """
        Normalize the recording volume
        """
        self.recording = Normalizer.stereo_normalization(self.recording)
        self.logger.debug(f"Downloaded file (volume normalized) sample count: {len(self.recording.get_array_of_samples()) / 2} [Note: should not alter the sample count]")
        return self

    def slice(self, methods=None):
        """
        Executes slicer methods in order defined in the methods list
        Args:
        :param methods: A dictionary of named slicing functions and parameters to clipify the downloaded file
        """
        self.slicer = Slicer(recording=self.recording, methods=methods, tagger=self.tagger, logger=self.logger)
        self.slicer.slice()
        self.clips = self.slicer.clip()

        return self

    def fade(self, fade_in_duration=DEFAULT_FADE_IN_MILISECONDS, fade_out_duration=DEFAULT_FADE_OUT_MILISECONDS):
        """
        Apply fade-in and fade-out to the clips
        Args:
        :param fade_in_duration: The number of miliseconds for the fade in
        :param fade_out_duration: The number of miliseconds for the fade out
        """
        for index, clip in enumerate(self.clips):
            self.clips[index]['samples'] = clip['samples'].fade_in(fade_in_duration).fade_out(fade_out_duration)
        return self

    def export(self, directory=EXPORT_ROOT):
        """
        Export the audio clips
        Args:
        :param directory: The location that the generated clips will be saved
        """
        title = self.tagger.get('title')

        for index, clip in enumerate(self.clips):
            Path(directory).mkdir(parents=True, exist_ok=True)
            filename = f"{directory}\\{title}.{index:05d}.{AUDIO_FILE_TYPE}"
            clip['samples'].export(filename, format=AUDIO_FILE_TYPE).close()
            self.tagger.set('from', f"{clip['from']:.3f}")
            self.tagger.set('to', f"{clip['to']:.3f}")
            self.tagger.write_tags(filename)
        return self
