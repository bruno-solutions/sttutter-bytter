"""
Slicer module
"""
from typing import List

import librosa
import pydub

from beat import BeatSlicer
from chaos import ChaosSlicer
from logger import Logger
from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval
from .voice import VoiceSlicer
from .volume import VolumeSlicer


class Slicer:
    """
    The primary object of the slicer module
    """

    def __init__(self, recording: pydub.AudioSegment, low_volume_threshold, min_miliseconds, max_miliseconds, max_clips, tagger, logger=Logger()):
        self.recording = recording
        self.low_volume_threshold = low_volume_threshold
        self.min_miliseconds = min_miliseconds
        self.max_miliseconds = max_miliseconds
        self.max_clips = max_clips
        self.tagger = tagger
        self.logger = logger

        self.sci: List[SampleClippingInterval] = []
        self.clips = []

    def get_clips(self):
        """
        Slice the source audio file into clips
        """
        self.logger.characteristics(self.recording)

        samples = self.recording.get_array_of_samples()
        frame_rate = self.recording.frame_rate

        for sci in self.sci:
            self.clips.append({'samples': samples[sci.begin:sci.end], 'sci': sci, 'begin': sci.begin / frame_rate, 'end': sci.end / frame_rate})

        return self.clips

    def slice_at_random(self):
        """
        Slices randomly (fun?!?...)
        """
        self.logger.characteristics(self.recording)
        self.sci.append(ChaosSlicer(self.recording).get())
        return self

    def slice_at_volume_change(self):
        """
        Slice on rapid volume changes (measuring every 10ms)
        """
        self.logger.characteristics(self.recording)
        self.sci.append(VolumeSlicer(self.recording, chunk_size=self.recording.frame_rate // 100).get())
        return self

    def slice_at_vocal_change(self):
        """
        Slice on vocal cues
        """
        self.logger.characteristics(self.recording)
        self.sci.append(VoiceSlicer(self.recording, 3, self.low_volume_threshold).get())
        return self

    def slice_at_beat(self):
        """
        Get every beat in a song and use that to input a bar of beats as critical times
        """
        self.logger.characteristics(self.recording)
        self.sci.append(BeatSlicer(self.recording).get())
        return self

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
        onset_env = librosa.onset.onset_strength(y=monaural_samples, sr=44100)
        return librosa.beat.tempo(onset_envelope=onset_env, sr=44100, aggregate=None)

    def debug_get_tempo(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        return librosa.beat.beat_track(y=monaural_samples, sr=44100)[0]

    def debug_get_beat_time(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        beats = librosa.beat.beat_track(y=monaural_samples, sr=44100)[1]
        return librosa.frames_to_time(beats, sr=44100)

    def debug_get_pitch(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        return librosa.yin(monaural_samples, fmin=40, fmax=2200, sr=22050, frame_length=2048)

    def debug_get_volume(self):
        monaural_samples = Normalizer.monaural_normalization(self.recording.get_array_of_samples(), self.recording.sample_width)
        return librosa.amplitude_to_db(S=monaural_samples, ref=0)
