"""
Slicer module
"""
from typing import List

import librosa
import pydub

from beat import BeatSlicer
from chaos import ChaosSlicer
from configuration import DEFAULT_MAX_CLIPS, DEFAULT_PAD_DURATION_MILISECONDS, DEFAULT_ATTACK_MILISECONDS, DEFAULT_BEAT_COUNT, DEFAULT_LOW_VOLUME_THRESHOLD_DECIBELS, DEFAULT_VOLUME_DRIFT_DECIBELS, DEFAULT_DETECTION_CHUNK_SIZE_MILISECONDS
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

    def slice_on_beat(self, stage, arguments):
        """
        Get every beat in a song and use that to input a bar of beats as critical times
        """
        beat_count = arguments['beat_count'] if 'beat_count' in arguments else DEFAULT_BEAT_COUNT
        attack_miliseconds = arguments['attack_miliseconds'] if 'attack_miliseconds' in arguments else DEFAULT_ATTACK_MILISECONDS
        max_clips = arguments['max_clips'] if 'max_clips' in arguments else DEFAULT_MAX_CLIPS

        self.sci.append(BeatSlicer(self.recording, stage, beat_count=beat_count, attack_miliseconds=attack_miliseconds, max_clips=max_clips).get())

    def slice_at_random(self, stage, arguments):
        """
        Slice randomly
        """
        pad_miliseconds = arguments['pad_miliseconds'] if 'pad_miliseconds' in arguments else DEFAULT_PAD_DURATION_MILISECONDS
        max_clips = arguments['max_clips'] if 'max_clips' in arguments else DEFAULT_MAX_CLIPS

        self.sci.append(ChaosSlicer(self.recording, stage, pad_miliseconds=pad_miliseconds, max_clips=max_clips).get())

    def slice_on_vocal_change(self, stage, arguments):
        """
        Slice on vocal cues
        """
        passes = arguments['passes'] if 'passes' in arguments else 1
        model = arguments['model'] if 'model' in arguments else 0
        detection_chunk_size_miliseconds = arguments['detection_chunk_size_miliseconds'] if 'detection_chunk_size_miliseconds' in arguments else DEFAULT_DETECTION_CHUNK_SIZE_MILISECONDS
        low_volume_threshold_decibels = arguments['low_volume_threshold_decibels'] if 'low_volume_threshold_decibels' in arguments else DEFAULT_LOW_VOLUME_THRESHOLD_DECIBELS
        volume_drift_decibels = arguments['volume_drift_decibels'] if 'volume_drift_decibels' in arguments else DEFAULT_VOLUME_DRIFT_DECIBELS
        max_clips = arguments['max_clips'] if 'max_clips' in arguments else DEFAULT_MAX_CLIPS

        self.sci.append(VocalSlicer(self.recording, stage, passes=passes, model=model, detection_chunk_size_miliseconds=detection_chunk_size_miliseconds, low_volume_threshold_decibels=low_volume_threshold_decibels, volume_drift_decibels=volume_drift_decibels, max_clips=max_clips, logger=self.logger).get())

    def slice_on_volume_change(self, stage, arguments):
        """
        Slice on rapid volume changes (measuring every 10ms)
        """
        detection_chunk_size_miliseconds = arguments['detection_chunk_size_miliseconds'] if 'detection_chunk_size_miliseconds' in arguments else DEFAULT_DETECTION_CHUNK_SIZE_MILISECONDS
        low_volume_threshold_decibels = arguments['low_volume_threshold_decibels'] if 'low_volume_threshold_decibels' in arguments else DEFAULT_LOW_VOLUME_THRESHOLD_DECIBELS
        volume_drift_decibels = arguments['volume_drift_decibels'] if 'volume_drift_decibels' in arguments else DEFAULT_VOLUME_DRIFT_DECIBELS
        max_clips = arguments['max_clips'] if 'max_clips' in arguments else DEFAULT_MAX_CLIPS

        self.sci.append(VolumeSlicer(self.recording, stage, detection_chunk_size_miliseconds=detection_chunk_size_miliseconds, low_volume_threshold_decibels=low_volume_threshold_decibels, volume_drift_decibels=volume_drift_decibels, max_clips=max_clips).get())

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
