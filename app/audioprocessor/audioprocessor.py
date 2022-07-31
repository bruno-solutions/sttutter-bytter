"""
The main audio processing module
"""
from pathlib import Path
from typing import Optional

import loader
from clip import Clip
from configuration.configuration import Configuration
from file import rm_md, md
from logger import Logger
from normalizer import Normalizer
from slicer import Slicer
from tagger import Tagger


class AudioProcessor(object):
    """
    The class that orchestrates the audio processing methods
    """

    def __init__(self, preserve_cache: bool = True):
        """
        Download a video or audio recording from the internet and save only the audio to a file
            - mono frame: single sample value
            - stereo frame: sample value pair
        Args:
        :param preserve_cache: should downloaded source media files be kept after processing to prevent re-download later
        """
        import pydub

        rm_md(cache_root=(None if preserve_cache else Configuration().get('cache_root')), export_root=Configuration().get('export_root'), log_root=Configuration().get('log_root'), temp_root=Configuration().get('temp_root'))

        if preserve_cache:
            md(Configuration().get('cache_root'), 'Cache root')

        self.tagger: Tagger = Tagger()
        self.loader = loader.Loader(tagger=self.tagger)
        self.slicer = Slicer()

        self.recording: Optional[pydub.AudioSegment] = None
        self.clips: [Clip] = []

    def load(self, uri: str):
        """
        Downloads or copies a file and converts it into a pydub AudioSegmant object
        Args:
        :param uri: The source Uniform Resource Identifier from which to extract the audio recording
        """
        self.recording, audio_file = self.loader.load(uri)
        Logger.properties(self.recording, "Post-download recording characteristics")

        self.trim()
        self.recording.export(audio_file, format=Configuration().get('output_file_type')).close()
        self.tagger.write_audio_file_tags(audio_file)
        Logger.properties(self.recording, "Post-trim recording characteristics")
        return self

    def trim(self):
        import pydub

        def trim(recording: pydub.AudioSegment):
            import pydub.silence

            trim.call += 1
            silence_ms: int = pydub.silence.detect_leading_silence(recording, silence_threshold=-50.0, chunk_size=10)
            recording = recording[silence_ms + 1:].reverse()

            if Configuration().get('log_debug'):
                debug_file_name: str = f"{Configuration().get('temp_root')}\\{'leading' if trim.call == 1 else 'leading.and.trailing'}.trim.wav"
                (recording.reverse() if 1 == trim.call else recording).export(debug_file_name, format=Configuration().get('output_file_type')).close()
                self.tagger.write_audio_file_tags(debug_file_name)  # in case we want to keep the file

            Logger.debug(f"Trimmed {silence_ms} ms of {'leading' if trim.call == 1 else 'trailing'} silence from the recording")
            return recording

        Logger.properties(self.recording, "Pre-trim recording characteristics:")
        trim.call = 0
        self.recording = trim(trim(self.recording))

        Logger.properties(self.recording, "Post-trim recording characteristics")
        Logger.debug("Note: sample count is very likely to be less than the prior sample count")
        return self

    def normalize(self):
        """
        Normalize the recording volume
        """
        Logger.properties(self.recording, "Pre-normalization recording characteristics:")
        self.recording = Normalizer.stereo_normalization(self.recording)
        Logger.properties(self.recording, "Post-normalization recording characteristics")
        Logger.debug("Note: sample count should not be less than the prior sample count")
        return self

    def slice(self, logic: [{}] = None):
        """
        Executes slicer methods in order defined in the methods list
        """
        logic = logic if logic is not None else Configuration().get('logic')
        Logger.separator(mode='debug')
        self.clips = self.slicer.slice(recording=self.recording, logic=logic).get()
        return self

    def fade(self, fade_in_duration: int = None, fade_out_duration: int = None):
        """
        Apply fade-in and fade-out to the clips
        Args:
        :param fade_in_duration: The number of miliseconds for the fade in
        :param fade_out_duration: The number of miliseconds for the fade out
        """

        fade_in_duration = fade_in_duration if fade_in_duration is not None else Configuration().get('fade_in_miliseconds')
        fade_out_duration = fade_out_duration if fade_out_duration is not None else Configuration().get('fade_out_miliseconds')

        for clip in self.clips:
            clip.segment = getattr(clip, "segment").fade_in(fade_in_duration).fade_out(fade_out_duration)

        return self

    def export(self):
        """
        Export the audio clips
        """
        export_root = Configuration().get('export_root')
        for index, clip in enumerate(self.clips):
            Path(export_root).mkdir(parents=True, exist_ok=True)
            filename = f"{export_root}\\{self.tagger.get('title')}.{index:05d}.{Configuration().get('output_file_type')}"
            getattr(clip, "segment").export(filename, format=Configuration().get('output_file_type')).close()
            self.tagger.set('source time indexes', f"{getattr(clip, 'begin')['time']:.3f}:::{getattr(clip, 'end')['time']:.3f}")
            self.tagger.set('source samples', f"{getattr(clip, 'begin')['index']:0.0f}:::{getattr(clip, 'end')['index']:0.0f}")
            self.tagger.write_audio_file_tags(filename)
        return self
