"""
Slicer module
"""

import random

import librosa
import numpy

from .critical import CriticalTimeIndexes
from .voice import VoiceSlicer
from .volume import VolumeSlicer


class Slicer:
    """
    The primary object of the slicer module
    """
    def __init__(self, sample_rate, duration, threshold, samples, count, tagger):
        self.sample_rate = sample_rate
        self.duration = duration
        self.threshold = threshold
        self.samples = samples
        self.count = count

        self.critical = CriticalTimeIndexes()
        self.clips = []

        self.tagger = tagger

        def monaural_normalization():
            """
            Converts the track values into librosa-compatible format
            int16 or int32 values to float values between -1. and 1.
            """
            stereo = numpy.array(self.samples.get_array_of_samples())
            left_channel = stereo[::2]
            right_channel = stereo[1::2]
            monaural = (left_channel + right_channel) / 2

            # Convert int16 or int32 data to float (-1. ~ 1.)
            return monaural / (1 << (self.samples.sample_width * 8) - 1)

        self.monaural_samples = monaural_normalization()

    def slice(self):
        """
        Slice the source audio file into clips
        """
        for interval in self.critical.interval:
            self.clips.append(self.samples[interval[0]:interval[1]])

        return self

    def slice_at_random(self):
        """
        Create slices at random
        This slicer method is meant to be a template for the creation of other slicer methods
        """
        # Access data, equivalent to data=librosa.load()
        # Alternatively, self.data can be used in place of 'data' directly

        for index in range(self.count):
            source_duration_ms = int(self.samples.duration_seconds * 1000)
            clip_start_ms = random.randint(0, source_duration_ms - 250)  # the start of source to 250ms before the end of source
            clip_end_ms = clip_start_ms + random.randint(250, source_duration_ms - clip_start_ms)  # 250ms up to the (source duration - the start of the clip)

        return self

    def slice_at_volume_change(self):
        """
        Slice the audio at moments of rapid volume changes
        """
        VolumeSlicer(self.monaural_samples).write_critical_time(self.critical.cti)
        return self

    def slice_at_voice(self):
        """
        Slice the audio according to the vocals of a song
        """
        VoiceSlicer(self.sample_rate, self.duration, self.threshold).write_critical_time(self.critical.cti)
        self.critical.intervals()
        return self

    def slice_at_beats(self):
        """
        Get every beat in a song and use that to input a bar of beats as critical times
        """
        frames = librosa.beat.beat_track(y=self.monaural_samples, sr=self.sample_rate)[1]

        # Change the beats from frames to time (ms)
        duration = librosa.frames_to_time(frames, sr=self.sample_rate) * 1000

        # Append every beat to the CTIs
        for i in range(1, len(frames)):
            self.critical.append(cti=[duration[i], duration[i - 1]])

        # Append every fourth beat to the CTIs
        # for i in range(4, len(frames), 8):
        #     self.critical.append(item=[frames[i - 4], frames[i] + 500])

        self.critical.intervals()
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
        onset_env = librosa.onset.onset_strength(y=self.monaural_samples, sr=44100)
        return librosa.beat.tempo(onset_envelope=onset_env, sr=44100, aggregate=None)

    def debug_get_tempo(self):
        return librosa.beat.beat_track(y=self.monaural_samples, sr=44100)[0]

    def debug_get_beat_time(self):
        beats = librosa.beat.beat_track(y=self.monaural_samples, sr=44100)[1]
        return librosa.frames_to_time(beats, sr=44100)

    def debug_get_pitch(self):
        return librosa.yin(self.monaural_samples, fmin=40, fmax=2200, sr=22050, frame_length=2048)

    def debug_get_volume(self):
        return librosa.amplitude_to_db(S=self.monaural_samples, ref=0)
