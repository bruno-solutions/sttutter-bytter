"""
Slicer module
"""

import random

import librosa
import numpy
import pydub
from pydub.utils import register_pydub_effect

from .critical import CriticalTimeIndexes
from .voice import VoiceSlicer
from .volume import VolumeChangeDetector


class Slicer:
    """
    The primary object of the slicer module
    """

    def __init__(self, sample_rate, duration, threshold, base_seg, count):
        self.sample_rate = sample_rate
        self.duration = duration
        self.threshold = threshold
        self.base_seg = base_seg
        self.count = count

        self.data = None
        self.normalize_amplitudes()
        self.critical = CriticalTimeIndexes()
        self.clips = []

    def normalize_amplitudes(self):
        """
        Converts the track values into librosa-compatible format
        int16 or int32 values to float values between -1. and 1.
        """

        stereo_track = numpy.array(self.base_seg.get_array_of_samples())
        left_track = stereo_track[::2]
        right_track = stereo_track[1::2]
        mono_track = (left_track + right_track) / 2

        # Convert int16 or int32 data to float (-1. ~ 1.)
        self.data = mono_track / (1 << (self.base_seg.sample_width * 8) - 1)

    @classmethod
    def invoke_slicers(cls, slicer_methods):
        """
        A method invoker that wraps and registers a custom slicer method in pydub's effects list
        """

        if isinstance(slicer_methods, dict):
            for named_method in slicer_methods.items():
                cls.invoke_slicers(named_method)

        elif isinstance(slicer_methods, tuple):
            name, method = slicer_methods

            @pydub.utils.register_pydub_effect(name)
            def slicer_method_wrap(sample_rate, duration, threshold, seg, count, *args, **kwargs):
                return getattr(cls(sample_rate, duration, threshold, seg, count), method)(*args, **kwargs).generate_clips().sliced_audio_segments

        else:
            raise TypeError

    def generate_clips(self):
        """
        Slicing the source audio file into clips
        """

        for interval in self.critical.interval:
            self.clips.append(self.base_seg[interval[0]:interval[1]])

        return self

    def slice_at_random(self):
        """
        Create slices at random.
        This slicer method is meant to be a template for the creation of other slicer methods.
        """

        # Access data, equivalent to data=librosa.load()
        # Alternatively, self.data can be used in place
        # of 'data' directly.

        # The total amount of clips desired is stored in self.count

        for index in range(self.count):
            # Calculate random range.
            duration_ms = int(self.base_seg.duration_seconds * 1000)
            start_ms = random.randint(0, duration_ms - 1000)
            end_ms = start_ms + random.randint(1000, 10000)  # 1 to 10 seconds long.

            # Append clip ranges to self.intervals.

            raise SyntaxError("PENDING CHANGE: Append to self.critical instead of self.intervals")

            # e.g.
            #   self.critical.append({
            #       "type": "major_volume_change",
            #       "index": _time,
            #       "weight": _weight
            #   })

        return self

    def slice_at_volume_change(self):
        """
        Slice the audio at moments of rapid volume changes
        """

        VolumeChangeDetector(self.data).write_critical_time(self.critical.cti)
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

        frames = librosa.beat.beat_track(y=self.data, sr=self.sample_rate)[1]

        # Change the beats from frames to time (ms)
        duration = librosa.frames_to_time(frames, sr=self.sample_rate) * 1000

        # Append every beat to the CTIs
        for i in range(1, len(frames)):
            self.critical.append(item=[duration[i], duration[i - 1]])

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
        onset_env = librosa.onset.onset_strength(y=self.data, sr=44100)
        return librosa.beat.tempo(onset_envelope=onset_env, sr=44100, aggregate=None)

    def debug_get_tempo(self):
        return librosa.beat.beat_track(y=self.data, sr=44100)[0]

    def debug_get_beat_time(self):
        beats = librosa.beat.beat_track(y=self.data, sr=44100)[1]
        return librosa.frames_to_time(beats, sr=44100)

    def debug_get_pitch(self):
        return librosa.yin(self.data, fmin=40, fmax=2200, sr=22050, frame_length=2048)

    def debug_get_volume(self):
        return librosa.amplitude_to_db(S=self.data, ref=0)
