"""
The main audio processing module
"""
import hashlib
import json
from pathlib import Path

import pydub
from pydub.utils import register_pydub_effect

import downloader
import file
from configuration import DEFAULT_EXTERNAL_DOWNLOADER, AUDIO_FILE_TYPE, DEFAULT_DURATION, DEFAULT_THRESHOLD, DEFAULT_CLIP_LIMIT, DEFAULT_SAMPLE_RATE, CACHE_ROOT, METADATA_FILE_TYPE, DEFAULT_FADE_IN_DURATION, DEFAULT_FADE_OUT_DURATION, EXPORT_ROOT
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
        """
        self.url = None
        self.download_file_name = None
        self.audio_file_name = None
        self.metadata_file_name = None

        self.sample_rate = sample_rate

        self.external_downloader = external_downloader
        self.normalizer = Normalizer()
        self.logger = logger
        self.recording = None
        self.tagger = None

        self.information = {}

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
        self.download_file_name = CACHE_ROOT + '\\' + hashlib.md5(url.encode('utf-8')).hexdigest().upper()
        self.audio_file_name = self.download_file_name + '.' + AUDIO_FILE_TYPE
        self.metadata_file_name = self.download_file_name + '.' + METADATA_FILE_TYPE

        self.information = downloader.download(self.url, directory=CACHE_ROOT, filename=self.download_file_name, logger=self.logger, external_downloader=self.external_downloader)
        self.recording = pydub.AudioSegment.from_file(self.audio_file_name).set_frame_rate(self.sample_rate)
        print(f"audioprocessor.py download() sample rate: {self.sample_rate}")
        print(f"audioprocessor.py download() frame rate: {self.recording.frame_rate}")
        print(f"audioprocessor.py download() sample count: {len(self.recording.get_array_of_samples()) / 2}")
        print(f"audioprocessor.py download() sample count: {(len(self.recording.get_array_of_samples()) / 2) / self.recording.frame_rate} {(((len(self.recording.get_array_of_samples()) / 2) / self.recording.frame_rate) // 60):0.0f}:{(((len(self.recording.get_array_of_samples()) / 2) // self.recording.frame_rate) % 60):0.0f}")
        return self

    def metadata(self):
        with open(self.metadata_file_name) as json_file:
            self.tagger = Tagger(json.load(json_file))
            self.tagger.write_tags(self.audio_file_name)
        return self

    def normalize(self):
        """
        Normalize recording volume
        """
        print(f"audioprocessor.py before self.normalizer.normalize() sample count: {len(self.recording.get_array_of_samples()) / 2}")
        self.recording = self.normalizer.normalize(self.recording)
        print(f"audioprocessor.py after self.normalizer.normalize() sample count: {len(self.recording.get_array_of_samples()) / 2}")
        return self

    def slice(self, slicers, duration=DEFAULT_DURATION, threshold=DEFAULT_THRESHOLD, clip_limit=DEFAULT_CLIP_LIMIT):
        """
        Loads and executes the slicer module
        Args:
            :param slicers: A dictionary of named slicing functions registered with pydub to clipify the downloaded file
            :param duration:
            :param threshold:
            :param clip_limit:
        """
        slicer_names = []

        def register(remaining_slicers):
            """
            Registers custom slicer methods from this Slicer class in pydub's effects list
            """
            if isinstance(remaining_slicers, dict):
                for named_method in remaining_slicers.items():
                    register(named_method)
                return

            if isinstance(remaining_slicers, tuple):
                name, method = remaining_slicers

                # https://github.com/jiaaro/pydub/blob/master/pydub/utils.py#LC108
                # https://github.com/jiaaro/pydub/blob/master/pydub/effects.py

                @register_pydub_effect(name)
                def registered_slicer(rate, duration, threshold, samples, count, *args, **kwargs):
                    slicer = Slicer(self.audio_file_name, rate, duration, threshold, samples, count, self.tagger)  # instantiate a Slicer object
                    getattr(slicer, method)(*args, **kwargs)  # call the registered slicer method on the Slicer object
                    return slicer.slice().clips  # return the clips generated by the registered slicer method

                slicer_names.append(name)
                return

            raise TypeError

        register(slicers)

        if 0 == len(slicer_names):
            raise RuntimeError("You didn't provice any slicers")

        for slicer_name in slicer_names:
            self.clips.extend(getattr(pydub.AudioSegment, slicer_name)(self.sample_rate, duration, threshold, self.recording, clip_limit))

        return self

    def fade(self, fade_in_duration=DEFAULT_FADE_IN_DURATION, fade_out_duration=DEFAULT_FADE_OUT_DURATION):
        """
        Apply fade-in and fade-out
        """
        for index, clip in enumerate(self.clips):
            self.clips[index]['samples'] = clip['samples'].fade_in(fade_in_duration).fade_out(fade_out_duration)
        return self

    def export(self, directory=EXPORT_ROOT):
        """
        Export the audio clips
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
