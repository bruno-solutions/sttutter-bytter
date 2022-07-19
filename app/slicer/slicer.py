"""
Slicer module
"""
import re
from typing import List

import librosa
import pydub

from beat import BeatSlicer
from chaos import ChaosSlicer
from configuration import DEFAULT_CLIPS, DEFAULT_ATTACK_MILISECONDS, DEFAULT_BEAT_COUNT, DEFAULT_LOW_VOLUME_THRESHOLD_DECIBELS, DEFAULT_VOLUME_DRIFT_DECIBELS, DEFAULT_DETECTION_CHUNK_SIZE_MILISECONDS, DEFAULT_CLIP_SIZE_MILISECONDS
from interval import SimpleIntervalSlicer
from logger import Logger
from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval
from .vocal import VocalSlicer
from .volume import VolumeSlicer


class Slicer:
    """
    The primary object of the slicer module
    """

    def __init__(self, recording: pydub.AudioSegment, methods=None, logger=Logger()):
        self.recording: pydub.AudioSegment = recording
        self.methods = methods if methods is not None else []
        self.logger = logger if logger is not None else Logger()

        self.sci: List[SampleClippingInterval] = []

    def set(self, name, value):
        setattr(self, name, value)

        return self

    def slice(self):
        """
        Apply registered slicer methods to generate the sample clipping intervals of the recording
        """
        if 0 == len(self.methods):
            raise RuntimeError("You didn't provide any slicer methods")

        self.sci = []

        self.logger.debug("Slicing sample clipping intervals from the recording")

        for stage, slicer in enumerate(self.methods):  # execution each slicer is a "stage" in the processing of the source recording
            try:
                method_name = slicer['method']
            except AttributeError:
                self.logger.warning(f"Attribute 'method' not defined on slicer[{stage}]")
                self.logger.warning(f"Available methods are: 'slice_on_beat', 'slice_at_random', 'slice_on_vocal_change', 'slice_on_volume_change'")
                continue

            try:
                method = getattr(Slicer, method_name)
            except AttributeError:
                self.logger.warning(f"No slicer method named '{method_name}' is avaialable in the slicer module, referenced in slicer[{stage}]")
                self.logger.warning(f"Available methods are: 'slice_on_beat', 'slice_at_random', 'slice_on_vocal_change', 'slice_on_volume_change'")
                continue

            try:
                arguments = slicer['arguments']
            except KeyError:
                self.logger.debug(f"'arguments' not provided for '{method_name}', using default parameter values")
                arguments = {}

            self.logger.properties(self.recording, f"Pre-stage:{stage} [{method_name}] slicing recording characteristics")
            method(self, stage, arguments)
            self.logger.properties(self.recording, f"Post-stage:{stage} [{method_name}] slicing recording characteristics")

        self.logger.debug(f"Sliced {len(self.sci)} sample clipping intervals from the recording")

        return self

    def clip(self):
        """
        Generate audio segment clips from the recording based upon the sample clipping intervals determined by slice()
        """
        self.logger.properties(self.recording, "Clip creation recording characteristics")

        samples = self.recording.get_array_of_samples()
        frame_rate = self.recording.frame_rate

        clips = []

        for sci in self.sci:
            clips.append({'samples': samples[sci.begin:sci.end], 'source': {'begin': {'sample': sci.begin, 'time': sci.begin / frame_rate}, 'end': {'sample': sci.end, 'time': sci.begin / frame_rate}}})

        return clips

    def to_decibels(self, value):
        if isinstance(value, str):
            pass
        return value

    def to_sample_index(self, value):
        if isinstance(value, str):
            pass
        return value

    def to_miliseconds(self, value):
        if isinstance(value, int) or isinstance(value, float):
            return len(self.recording) * value if 0 <= value <= 1 else value  # decimal percentage or miliseconds

        note = "Durations are numeric (int or float) values or strings ending with one of the following: 's', 'sec', 'secs', 'seconds', 'ms', 'miliseconds', or '%'"

        if not isinstance(value, str):
            self.logger.warning(f"Duration argument type not valid {value} of {type(value)} [Fixup: returning 0]")
            self.logger.warning(note)
            return 0

        string = value.replace(' ', '')
        if '' == string:
            string = '0'
        parts = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
        number = float(parts[1])
        units = parts[2]
        if '' == units and 0 <= number <= 1:  # decimal percentage
            number = len(self.recording) * number
        elif '%' == units:
            number = len(self.recording) * number / 100
        elif 's' == units or 'sec' == units or 'secs' == units or 'seconds' == units:
            number = number * 1000
        elif '' == units or 'ms' == units or 'miliseconds' == units:
            number = number
        else:
            self.logger.warning(f"Duration argument units invalid, {string} [Fixup: treating as {number} miliseconds]")
            self.logger.warning(note)
        return int(number)

    def parse_common_arguments(self, arguments):
        recording_length_in_miliseconds = len(self.recording)

        begin = self.to_miliseconds(arguments['begin']) if 'begin' in arguments else 0.0
        end = self.to_miliseconds(arguments['end']) if 'end' in arguments else recording_length_in_miliseconds
        clip_size: int = self.to_miliseconds(arguments['clip_size']) if 'clip_size' in arguments else DEFAULT_CLIP_SIZE_MILISECONDS
        clips: int = arguments['clips'] if 'clips' in arguments else DEFAULT_CLIPS

        note = "Note: use values between 0.0 and 1.0 ('100%') to calculate a percentage of the clip duration as the starting or stopping point for clip generation"

        if 0 > begin:
            self.logger.warning(f"Argument 'begin' {begin} invalid, must be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using 0 ms]")
            self.logger.warning(f"Omit or set the 'begin' argument to 0 to start at the first sample of the recording")
            begin = 0
            if note is not None:
                self.logger.warning(note)
                note = None
        if recording_length_in_miliseconds < begin:
            self.logger.warning(f"Argument 'end' {begin} invalid, must be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using {recording_length_in_miliseconds} ms]")
            begin = recording_length_in_miliseconds
            if note is not None:
                self.logger.warning(note)
                note = None
        if 0 > end:
            self.logger.warning(f"Argument 'end' {end} invalid, must be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using 0 ms]")
            end = 0
            if note is not None:
                self.logger.warning(note)
                note = None
        if recording_length_in_miliseconds < end:
            self.logger.warning(f"Argument 'end' {end} invalid must, be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using {recording_length_in_miliseconds} ms]")
            self.logger.warning(f"Omit or set the 'end' argument to 1 to stop at the last sample of the recording")
            end = recording_length_in_miliseconds
            if note is not None:
                self.logger.warning(note)
                note = None
        if begin > end:
            begin, end = end, begin
            self.logger.warning(f"Argument begin {end} and end {begin} were reversed [Fixup: using {begin},{end}]")

        if note is not None:
            self.logger.debug(note)

        return self.recording[begin:end], int(self.recording.frame_rate * begin / 1000), clip_size, clips

    def slice_on_beat(self, stage, arguments):
        """
        Get every beat in a song and use that to input a bar of beats as critical times
        """
        segment, begin, clip_size, clips = self.parse_common_arguments(arguments)
        beat_count = arguments['beat_count'] if 'beat_count' in arguments else DEFAULT_BEAT_COUNT
        attack_miliseconds = arguments['attack_miliseconds'] if 'attack_miliseconds' in arguments else DEFAULT_ATTACK_MILISECONDS

        self.sci.append(BeatSlicer(stage, segment, beat_count=beat_count, attack_miliseconds=attack_miliseconds, clips=clips).get())

    def slice_at_interval(self, stage, arguments):
        """
        Slice equally spaced clips based upon the clip size, the desired number of clips, and the duration of the downloaded audio recording
        """
        segment, base_sample_index, clip_size, clips = self.parse_common_arguments(arguments)
        self.sci += SimpleIntervalSlicer(stage, segment, base_sample_index=base_sample_index, clip_size=clip_size, clips=clips, logger=self.logger).get()

    def slice_at_random(self, stage, arguments):
        """
        Slice randomly (for those who are reckless)
        """
        segment, base_sample_index, clip_size, clips = self.parse_common_arguments(arguments)
        self.sci += ChaosSlicer(stage, segment, base_sample_index=base_sample_index, clip_size=clip_size, clips=clips, logger=self.logger).get()

    def slice_on_vocal_change(self, stage, arguments):
        """
        Slice on vocal cues
        """
        segment, begin, clip_size, clips = self.parse_common_arguments(arguments)
        passes = arguments['passes'] if 'passes' in arguments else 1
        model = arguments['model'] if 'model' in arguments else 0
        detection_chunk_size_miliseconds = arguments['detection_chunk_size_miliseconds'] if 'detection_chunk_size_miliseconds' in arguments else DEFAULT_DETECTION_CHUNK_SIZE_MILISECONDS
        low_volume_threshold_decibels = arguments['low_volume_threshold_decibels'] if 'low_volume_threshold_decibels' in arguments else DEFAULT_LOW_VOLUME_THRESHOLD_DECIBELS
        volume_drift_decibels = arguments['volume_drift_decibels'] if 'volume_drift_decibels' in arguments else DEFAULT_VOLUME_DRIFT_DECIBELS

        self.sci.append(VocalSlicer(stage, segment, passes=passes, model=model, detection_chunk_size_miliseconds=detection_chunk_size_miliseconds, low_volume_threshold_decibels=low_volume_threshold_decibels, volume_drift_decibels=volume_drift_decibels, clips=clips, logger=self.logger).get())

    def slice_on_volume_change(self, stage, arguments):
        """
        Slice on rapid volume changes (measuring every 10ms)
        """
        segment, begin, clip_size, clips = self.parse_common_arguments(arguments)
        detection_chunk_size_miliseconds = arguments['detection_chunk_size_miliseconds'] if 'detection_chunk_size_miliseconds' in arguments else DEFAULT_DETECTION_CHUNK_SIZE_MILISECONDS
        low_volume_threshold_decibels = arguments['low_volume_threshold_decibels'] if 'low_volume_threshold_decibels' in arguments else DEFAULT_LOW_VOLUME_THRESHOLD_DECIBELS
        volume_drift_decibels = arguments['volume_drift_decibels'] if 'volume_drift_decibels' in arguments else DEFAULT_VOLUME_DRIFT_DECIBELS

        self.sci.append(VolumeSlicer(stage, segment, detection_chunk_size_miliseconds=detection_chunk_size_miliseconds, low_volume_threshold_decibels=low_volume_threshold_decibels, volume_drift_decibels=volume_drift_decibels, clips=clips).get())

    #     def slice_at_major_pitch_change(self):
    #         """
    #         Output is in ms
    #         Identify major pitch change time
    #         return 4/173 or 23 ms if pitch change occurs at the first/second frame
    #         search pitch detection algorithm (PDA)
    #         Note:
    #             If multi-channel input is provided,
    #             frequency curves are estimated separately for each channel,
    #             so to prevent error, we might need to pass in single channel input
    #         """

    #         pitches = librosa.yin(self.data,fmin=40, fmax=2200, sr=22050, frame_length=2048)
    #         difference = math.fabs(pitches[2]-pitches[1])

    #         pos = -1
    #         for i in range(1, pitches.size-1):
    #             if (math.fabs(pitches[i+1]-pitches[i]))>difference:
    #                 difference = math.fabs(pitches[i+1]-pitches[i])
    #                 pos = i+1

    #         if pos == -1:
    #             return 4/173
    #         else:
    #             return pos * (4/173)
    #
    #     def slice_at_onset_detection(self):
    #         """
    #         Onset (major sound change) Detection (librosa has this exact function we can use)
    #         return an numpy array of onset appearances in time in ms
    #         only works for monophonic sound (I think this means single channel sound)
    #         """

    #         onsets = librosa.onset.onset_detect(y = self.data, sr = 44100, units ='time')
    #         scaled_onsets = onsets * 1000
    #         #return scaled_onsets
    #
    #     def slice_at_major_tempo_change(self):
    #          """
    #          Output is in ms
    #          Identify major tempo (beats per minute) change time
    #          return -1 if no tempo change
    #          return location of biggest tempo change
    #          Note that most songs could have the same tempo throughout
    #          """
    #
    #          onset_env = librosa.onset.onset_strength(y = self.data, sr=44100)
    #          tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=44100,aggregate=None)
    #
    #          difference = math.fabs(tempo[1]-tempo[0])
    #
    #          pos=-1
    #          for i in range(tempo.size-1):
    #              if (math.fabs(tempo[i+1]-tempo[i])) >= difference+2:
    #                  difference = math.fabs(tempo[i+1]-tempo[i])
    #                  pos = i+1
    #
    #          if difference == math.fabs(tempo[1]-tempo[0]):
    #              return -1
    #
    #          time_from_frame = librosa.frames_to_time(pos, sr=44100)
    #          return time_from_frame

    def debug_get_real_time_tempo(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording)
        onset_env = librosa.onset.onset_strength(y=monaural_samples, sr=self.recording.frame_rate)
        return librosa.beat.tempo(onset_envelope=onset_env, sr=self.recording.frame_rate, aggregate=None)

    def debug_get_tempo(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording)
        return librosa.beat.beat_track(y=monaural_samples, sr=self.recording.frame_rate)[0]

    def debug_get_beat_time(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording)
        beats = librosa.beat.beat_track(y=monaural_samples, sr=self.recording.frame_rate)[1]
        return librosa.frames_to_time(beats, sr=self.recording.frame_rate)

    def debug_get_pitch(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording)
        return librosa.yin(monaural_samples, fmin=40, fmax=2200, sr=self.recording.frame_rate, frame_length=2048)

    def debug_get_volume(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording)
        return librosa.amplitude_to_db(S=monaural_samples, ref=0)
