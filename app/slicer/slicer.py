"""
Slicer module
"""
from typing import List

import librosa
import pydub

from beat import BeatSlicer
from chaos import ChaosSlicer
from configuration import DEFAULT_MAX_CLIPS
from logger import Logger
from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval
from .voice import VoiceSlicer
from .volume import VolumeSlicer


class Slicer:
    """
    The primary object of the slicer module
    """

    def __init__(self, recording: pydub.AudioSegment, methods=None, tagger=None, logger=Logger()):
        self.recording = recording
        self.methods = methods if methods is not None else []
        self.tagger = tagger
        self.logger = logger

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

        for index, slicer in enumerate(self.methods):
            try:
                method = getattr(slicer, 'method')
            except AttributeError:
                self.logger.warning(f"Attribute 'method' not defined on slicer[{index}]")
                self.logger.warning(f"Available methods are:\n - 'slice_on_beat'\n - 'slice_at_random'\n - 'slice_on_vocal_change'\n - 'slice_on_volume_change'")
                continue

            try:
                method = getattr(Slicer, method)
            except AttributeError:
                self.logger.warning(f"No slicer method named '{method}' is avaialable in the slicer module, referenced in slicer[{index}]")
                self.logger.warning(f"Available methods are:\n - 'slice_on_beat'\n - 'slice_at_random'\n - 'slice_on_vocal_change'\n - 'slice_on_volume_change'")
                continue

            arguments = getattr(Slicer, 'arguments', None)

            self.logger.characteristics(self.recording)
            method(arguments)

        self.logger.debug(f"Sliced {len(self.sci)} sample clipping intervals from the recording")

        return self

    def clip(self):
        """
        Generate audio segment clips from the recording based upon the sample clipping intervals determined by slice()
        """
        self.logger.characteristics(self.recording)

        samples = self.recording.get_array_of_samples()
        frame_rate = self.recording.frame_rate

        clips = []

        for sci in self.sci:
            clips.append({'samples': samples[sci.begin:sci.end], 'source': {'begin': {'sample': sci.begin, 'time': sci.begin / frame_rate}, 'end': {'sample': sci.end, 'time': sci.begin / frame_rate}}})

        return clips

    def slice_on_beat(self, arguments):
        """
        Get every beat in a song and use that to input a bar of beats as critical times
        """
        self.sci.append(BeatSlicer(self.recording, beat_count=getattr(arguments, 'beat_count', [4]), attack_miliseconds=getattr(arguments, 'attack_miliseconds', 50), max_clips=getattr(arguments, 'max_clips', DEFAULT_MAX_CLIPS)).get())

    def slice_at_random(self, arguments):
        """
        Slice randomly (fun?!?... or maybe are you a deranged lunatic?)
        """
        self.sci.append(ChaosSlicer(self.recording, pad_miliseconds=getattr(arguments, 'pad_miliseconds', 250), max_clips=getattr(arguments, 'max_clips', DEFAULT_MAX_CLIPS)).get())

    def slice_on_vocal_change(self, arguments):
        """
        Slice on vocal cues
        """
        self.sci.append(VoiceSlicer(self.recording, target_clip_length_miliseconds=getattr(arguments, 'target_clip_length_miliseconds', 9000), low_volume_threshold_decibels=getattr(arguments, 'low_volume_threshold_decibels', -20.0), max_clips=getattr(arguments, 'max_clips', DEFAULT_MAX_CLIPS)).get())

    def slice_on_volume_change(self, arguments):
        """
        Slice on rapid volume changes (measuring every 10ms)
        """
        self.sci.append(VolumeSlicer(self.recording, detection_chunk_size_miliseconds=getattr(arguments, 'detection_chunk_size_miliseconds', 10), low_volume_threshold_decibels=getattr(arguments, 'low_volume_threshold_decibels', -20.0), volume_drift_decibels=getattr(arguments, 'volume_drift_decibels', 0.1), max_clips=getattr(arguments, 'max_clips', DEFAULT_MAX_CLIPS)).get())

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
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        onset_env = librosa.onset.onset_strength(y=monaural_samples, sr=self.recording.frame_rate)
        return librosa.beat.tempo(onset_envelope=onset_env, sr=self.recording.frame_rate, aggregate=None)

    def debug_get_tempo(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        return librosa.beat.beat_track(y=monaural_samples, sr=self.recording.frame_rate)[0]

    def debug_get_beat_time(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        beats = librosa.beat.beat_track(y=monaural_samples, sr=self.recording.frame_rate)[1]
        return librosa.frames_to_time(beats, sr=self.recording.frame_rate)

    def debug_get_pitch(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        return librosa.yin(monaural_samples, fmin=40, fmax=2200, sr=self.recording.frame_rate, frame_length=2048)

    def debug_get_volume(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        return librosa.amplitude_to_db(S=monaural_samples, ref=0)
