"""
The main audio processing module
"""
from pathlib import Path
from typing import Optional

import pydub.silence

import file
import loader
from configuration import DEFAULT_DOWNLOADER_MODULE, AUDIO_FILE_TYPE, DEFAULT_FRAME_RATE, CACHE_ROOT, DEFAULT_FADE_IN_MILISECONDS, DEFAULT_FADE_OUT_MILISECONDS, EXPORT_ROOT, TEMP_ROOT, LOG_DEBUG
from logger import Logger
from normalizer import Normalizer
from slicer import Slicer
from tagger import Tagger


class AudioProcessor:
    """
    The class that orchestrates the audio processing methods
    """

    def __init__(self, frame_rate: int = DEFAULT_FRAME_RATE, cache_root: str = CACHE_ROOT, downloader_module: str = DEFAULT_DOWNLOADER_MODULE, logger: Logger = None, preserve_cache: bool = True):
        """
        Download a video or audio recording from the internet and save only the audio to a file
            - mono frame: single sample value
            - stereo frame: sample value pair
        Args:
        :param frame_rate:        the audio frames per second to make the extracted audio file | None to use the default sample rate
        :param downloader_module: a library for YouTube Download to use for file download | None to use the built-in downloader
        :param logger:            user supplied logger class | None to use the built-in Logger
        :param preserve_cache:    should downloaded source media files be kept after processing to prevent re-download later
        """
        self.cache_root: str = cache_root
        self.frame_rate: int = frame_rate

        self.logger: Logger = logger if logger is not None else Logger()
        self.recording: Optional[pydub.AudioSegment] = None
        self.tagger: Tagger = Tagger()
        self.slicer: Optional[Slicer] = None

        self.loader = loader.Loader(frame_rate=frame_rate, downloader_module=downloader_module, tagger=self.tagger, logger=self.logger)

        self.clips: [] = []

        if preserve_cache:
            file.rm_md(cache_root=None)
        else:
            file.rm_md()

    def load(self, uri: str):
        """
        Downloads or copies a file and converts it into a pydub AudioSegmant object
        Args:
        :param uri: The source Uniform Resource Identifier from which to extract the audio recording
        """
        self.recording, audio_file = self.loader.load(uri)
        self.logger.properties(self.recording, "Post-download recording characteristics")

        self.trim()
        self.recording.export(audio_file, format=AUDIO_FILE_TYPE).close()
        self.tagger.write_audio_file_tags(audio_file)
        self.logger.properties(self.recording, "Post-trim recording characteristics")
        return self

    def trim(self):
        def trim(recording: pydub.AudioSegment):
            trim.call += 1
            silence_ms: int = pydub.silence.detect_leading_silence(recording, silence_threshold=-50.0, chunk_size=10)
            recording = recording[silence_ms + 1:].reverse()

            if LOG_DEBUG:
                debug_file_name: str = f"{TEMP_ROOT}\\{'leading' if trim.call == 1 else 'leading.and.trailing'}.trim.wav"
                (recording.reverse() if 1 == trim.call else recording).export(debug_file_name, format=AUDIO_FILE_TYPE).close()
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

    def slice(self, methods: [{}] = None):
        """
        Executes slicer methods in order defined in the methods list
        Args:
        :param methods: A dictionary of named slicing functions and parameters to clipify the downloaded file
        """
        self.logger.separator(mode='debug')
        self.slicer = Slicer(recording=self.recording, methods=methods, logger=self.logger)
        self.slicer.slice()
        self.clips = self.slicer.clip()
        return self

    def fade(self, fade_in_duration: int = DEFAULT_FADE_IN_MILISECONDS, fade_out_duration: int = DEFAULT_FADE_OUT_MILISECONDS):
        """
        Apply fade-in and fade-out to the clips
        Args:
        :param fade_in_duration: The number of miliseconds for the fade in
        :param fade_out_duration: The number of miliseconds for the fade out
        """
        for index, clip in enumerate(self.clips):
            self.clips[index]['samples'] = clip['samples'].fade_in(fade_in_duration).fade_out(fade_out_duration)
        return self

    def export(self, directory: str = EXPORT_ROOT):
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
            self.tagger.write_audio_file_tags(filename)
        return self
