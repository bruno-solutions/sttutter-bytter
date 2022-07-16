"""
The main audio processing module
"""
import hashlib
import json
from pathlib import Path

import pydub.silence

import downloader
import file
from configuration import DEFAULT_EXTERNAL_DOWNLOADER, AUDIO_FILE_TYPE, DEFAULT_FRAME_RATE, CACHE_ROOT, METADATA_FILE_TYPE, DEFAULT_FADE_IN_MILISECONDS, DEFAULT_FADE_OUT_MILISECONDS, EXPORT_ROOT, TEMP_ROOT, LOG_DEBUG
from logger import Logger
from normalizer import Normalizer
from slicer import Slicer
from tagger import Tagger


class AudioProcessor:
    """
    The class that orchestrates the audio processing methods
    """

    def __init__(self, frame_rate=DEFAULT_FRAME_RATE, external_downloader=DEFAULT_EXTERNAL_DOWNLOADER, logger=Logger(), preserve_cache=True):
        """
        Download a video or audio recording from the internet and save only the audio to a file
            - mono frame: single sample value
            - stereo frame: sample value pair
        Args:
        :param frame_rate:          The audio frames per second to make the extracted audio file | None to use the default sample rate
        :param external_downloader: A library for YouTube Download to use for file download | None to use the built-in downloader
        :param logger:              User supplied logger class | None to use the built-in Logger
        :param preserve_cache:      Should downloaded source media files be kept after processing to prevent re-download later
        """
        self.url = None
        self.download_file_name = None
        self.audio_file_name = None
        self.metadata_file_name = None

        self.frame_rate = frame_rate

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

        self.logger.debug(f"\nDowloading from {url} and setting the frame rate to: {self.frame_rate}")
        downloader.download(self.url, directory=CACHE_ROOT, filename=self.download_file_name, logger=self.logger, external_downloader=self.external_downloader)

        with open(self.metadata_file_name) as json_file:
            self.tagger = Tagger(json.load(json_file))

        self.recording = pydub.AudioSegment.from_file(self.audio_file_name)
        self.recording = self.recording.set_frame_rate(self.frame_rate)
        self.logger.characteristics(self.recording, "Post-download recording characteristics")
        self.trim()
        self.recording.export(self.audio_file_name, format=AUDIO_FILE_TYPE).close()
        self.logger.characteristics(self.recording, "Post-trim recording characteristics")

        self.tagger.write_tags(self.audio_file_name)
        return self

    def trim(self):
        def trim(recording: pydub.AudioSegment):
            trim.call += 1
            silence_ms = pydub.silence.detect_leading_silence(recording, silence_threshold=-50.0, chunk_size=10)
            recording = recording[silence_ms + 1:].reverse()

            if LOG_DEBUG:
                debug_file_name = f"{TEMP_ROOT}\\{'leading' if trim.call == 1 else 'leading.and.trailing'}.trim.wav"
                (recording if 1 == trim.call else recording.reverse()).export(debug_file_name, format=AUDIO_FILE_TYPE).close()
                self.tagger.write_tags(debug_file_name)  # in case we want to keep the file

            self.logger.debug(f"Trimmed {silence_ms} ms of {'leading' if trim.call == 1 else 'trailing'} silence from the recording")
            return recording

        self.logger.characteristics(self.recording, "Pre-trim recording characteristics:")
        trim.call = 0
        self.recording = trim(trim(self.recording))

        self.logger.characteristics(self.recording, "Post-trim recording characteristics - Note: sample count is very likely to be less than the prior sample count")
        return self

    def normalize(self):
        """
        Normalize the recording volume
        """
        self.logger.characteristics(self.recording, "Pre-normalization recording characteristics:")
        self.recording = Normalizer.stereo_normalization(self.recording)
        self.logger.characteristics(self.recording, "Post-normalization recording characteristics - Note: sample count should not be less than the prior sample count")
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
            self.tagger.set('source time indexes', f"{clip['source']['begin']['time']:.3f}:::{clip['source']['end']['time']:.3f}")
            self.tagger.set('source samples', f"{clip['source']['begin']['sample']:0.0f}:::{clip['source']['end']['sample']:0.0f}")
            self.tagger.write_tags(filename)
        return self
