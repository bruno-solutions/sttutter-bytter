"""
The main audio processing module
"""
from pathlib import Path
from typing import Optional

import pydub.silence

import loader
from clip import Clip
from configuration.configuration import Configuration
from file import rm_md
from logger import Logger
from normalizer import Normalizer
from slicer import Slicer
from tagger import Tagger


class AudioProcessor(object):
    """
    The class that orchestrates the audio processing methods
    """

    def __init__(self, frame_rate: int = Configuration().get('frame_rate'), downloader_module: str = Configuration().get('downloader_module'), preserve_cache: bool = True, cache_root: str = Configuration().get('cache_root'), export_root: str = Configuration().get('export_root'), logger: Logger = None):
        """
        Download a video or audio recording from the internet and save only the audio to a file
            - mono frame: single sample value
            - stereo frame: sample value pair
        Args:
        :param frame_rate:        the audio frames per second to make the extracted audio file
        :param downloader_module: a library for YouTube Download to use for file download | None to use the built-in downloader
        :param preserve_cache:    should downloaded source media files be kept after processing to prevent re-download later
        :param cache_root:        the directory in which to store download and preprocessed media files
        :param export_root:       the location to which generated clips will be saved
        :param logger:            class to send debug, warning, and error messages to the console and log file
        """
        rm_md(cache_root=(None if preserve_cache else cache_root), export_root=export_root, logger=logger)

        self.cache_root: str = cache_root
        self.export_root: str = export_root

        self.logger: Logger = logger if logger is not None else Logger()
        self.tagger: Tagger = Tagger()
        self.loader = loader.Loader(frame_rate=frame_rate, downloader_module=downloader_module, tagger=self.tagger, logger=self.logger)
        self.slicer = Slicer(logger=self.logger)

        self.recording: Optional[pydub.AudioSegment] = None
        self.clips: [Clip] = []

    def load(self, uri: str):
        """
        Downloads or copies a file and converts it into a pydub AudioSegmant object
        Args:
        :param uri: The source Uniform Resource Identifier from which to extract the audio recording
        """
        self.recording, audio_file = self.loader.load(uri)
        self.logger.properties(self.recording, "Post-download recording characteristics")

        self.trim()
        self.recording.export(audio_file, format=Configuration().get('output_file_type')).close()
        self.tagger.write_audio_file_tags(audio_file)
        self.logger.properties(self.recording, "Post-trim recording characteristics")
        return self

    def trim(self):
        def trim(recording: pydub.AudioSegment):
            trim.call += 1
            silence_ms: int = pydub.silence.detect_leading_silence(recording, silence_threshold=-50.0, chunk_size=10)
            recording = recording[silence_ms + 1:].reverse()

            if Configuration().get('log_debug'):
                debug_file_name: str = f"{Configuration().get('temp_root')}\\{'leading' if trim.call == 1 else 'leading.and.trailing'}.trim.wav"
                (recording.reverse() if 1 == trim.call else recording).export(debug_file_name, format=Configuration().get('output_file_type')).close()
                self.tagger.write_audio_file_tags(debug_file_name)  # in case we want to keep the file

            self.logger.debug(f"Trimmed {silence_ms} ms of {'leading' if trim.call == 1 else 'trailing'} silence from the recording")
            return recording

        self.logger.properties(self.recording, "Pre-trim recording characteristics:")
        trim.call = 0
        self.recording = trim(trim(self.recording))

        self.logger.properties(self.recording, "Post-trim recording characteristics")
        self.logger.debug("Note: sample count is very likely to be less than the prior sample count")
        return self

    def normalize(self):
        """
        Normalize the recording volume
        """
        self.logger.properties(self.recording, "Pre-normalization recording characteristics:")
        self.recording = Normalizer.stereo_normalization(self.recording)
        self.logger.properties(self.recording, "Post-normalization recording characteristics")
        self.logger.debug("Note: sample count should not be less than the prior sample count")
        return self

    def slice(self, logic: [{}] = Configuration().mutable_logic):
        """
        Executes slicer methods in order defined in the methods list
        Args:
        :param logic: A dictionary of named slicing functions and parameters to clipify the downloaded file
        """
        self.logger.separator(mode='debug')
        self.clips = self.slicer.slice(recording=self.recording, logic=logic).get()
        return self

    def fade(self, fade_in_duration: int = Configuration().get('fade_in_miliseconds'), fade_out_duration: int = Configuration().get('fade_out_miliseconds')):
        """
        Apply fade-in and fade-out to the clips
        Args:
        :param fade_in_duration: The number of miliseconds for the fade in
        :param fade_out_duration: The number of miliseconds for the fade out
        """
        for index, clip in enumerate(self.clips):
            self.clips[index]['samples'] = clip['samples'].fade_in(fade_in_duration).fade_out(fade_out_duration)
        return self

    def export(self):
        """
        Export the audio clips
        """
        for index, clip in enumerate(self.clips):
            Path(self.export_root).mkdir(parents=True, exist_ok=True)
            filename = f"{self.export_root}\\{self.tagger.get('title')}.{index:05d}.{Configuration().get('output_file_type')}"
            clip['samples'].export(filename, format=Configuration().get('output_file_type')).close()
            self.tagger.set('source time indexes', f"{clip['source']['begin']['time']:.3f}:::{clip['source']['end']['time']:.3f}")
            self.tagger.set('source samples', f"{clip['source']['begin']['sample']:0.0f}:::{clip['source']['end']['sample']:0.0f}")
            self.tagger.write_audio_file_tags(filename)
        return self
