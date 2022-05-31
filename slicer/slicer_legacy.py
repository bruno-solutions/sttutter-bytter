import array
import math
import os
import re
from email.mime import audio
from email.utils import format_datetime
from msilib.schema import Class
from unittest import result

import librosa
import numpy as np
from pydub import AudioSegment
from typing_extensions import Self

# import requests
# MAIN
if not os.path.exists("./audioTemp"):
    os.mkdir("audioTemp")


class Slicer:
    """
    Slicer
    """

    def __init__(self):
        pass

    # unfunished since Leveling function is not finished
    @staticmethod
    def get_leveled_audio_file():
        """
        Get Leveled AudioFile
        return a AudioSegment object
        """

        # From downloader file
        # name = stWavFile.wav
        return AudioSegment.from_file("stWavFile.wav", format="wav")

    @staticmethod
    def process_audio_clip(clip_list):
        """
        pydub(fade in/ fade out)
        input: a list of clips will be processed
        """

        ### Add fade in and fade out to clips
        for clip in clip_list:
            clip.fade_in(250)
            clip.fade_out(250)

    @staticmethod
    def get_copy_of_audio(target):
        """"
        Since the audio change will fundmentally change the original file,
        this method is help to get a copy of original file.
        """

        # file audioTemp is exist from main function
        target.export("audioTemp\\temp.wav", format="wav")
        re = AudioSegment.from_file("audioTemp\\temp.wav", format="wav")
        os.remove("audioTemp\\temp.wav")
        return re

    @staticmethod
    def cut_audio(critical_time, target):
        """
        input: List of pair of critical times
        output: push all clips to AllAudioClips file.
        """

        ### Use critical times to slice the audio clip into clips
        re = []
        for pair in critical_time:
            re.append(Slicer.get_copy_of_audio(target)[pair[0]: pair[1]])
        return re

    @staticmethod
    def push_out_clips(clip_list):
        """
        input: an array of cutted audioSegment Objects
        push out all audio clip into output file with {certain} format
        """

        ### If AllAudioClips directory does not exist then make it
        if not os.path.exists("AllAudioClips"):
            os.makedirs("AllAudioClips")

        ### Using name_roller to help in making
        name = Slicer.name_roller()

        ### Make all names uniform except for the number
        for segment in clip_list:
            segment.export("AllAudioClips\\" + str(next(name)) + ".wav", format="wav")

    @staticmethod
    def name_roller():
        """A naming helper of push_out_clips()"""
        i = 0

        while True:
            yield i
            i += 1

    # Lyrics(Shazam/MusicMixer(testing))
    # DrumSetChange/beatChage(librosa/AudioOwl)
    # pitchChange(librosa/AudioOwl)
    # We could mix match difference major change in pitch, beat, volumne to create more ways of slicing (like they can be different start, end points)
    @staticmethod
    def get_critical_time_index(max_duration, min_duration, clips_nums=1):
        """
        input:
            max_duration: Maximum time duration of a single clips
            min_duration: Minimum time duration of a single clips
            clips_nums: number of clips will be returned. Default @ 1
        return: a list of pair list of critical times in ms
        e.g: [[star1, end1],[star2, end2], [star3, end3]...]
        """

        # # sample code, work as place holder
        # temp = [
        #     Slicer.major_volume_change(),
        #     Slicer.major_tempo_change(),
        #     Slicer.major_pitch_change()
        # ]
        # self.append(future_major_pitch_array[0],
        # future_major_volume_array[0],
        # Slicer.major_tempo_change())

        for i in Slicer.onset_detection():
            # in future: self.append(i)
        re = []

        ### Adjust the length for stereo and then append it to self
        for i in range(int(len(temp) / 2)):
            # in future: re.append([self[i * 2], self[i * 2 + 1]])

        ### Return critical time
        return re

    @staticmethod
    def get_lyrics_change_times():
        pass

    @staticmethod
    def major_pitch_change(data_file_array):
        """
        Output is in ms
        Identify major pitch change time
        search pitch detection algorithm (PDA)
        Note:
            If multi-channel input is provided, frequency curves are estimated separately for each channel
            So to prevent error, we might need to pass in single channel input
        """

        y, sr = data_file_array  ###load in the data for the files via a data array

        ### Calculate pitches via librosa
        pitches = librosa.yin(y, fmin=65, fmax=2093, frame_length=20480)

        ### Calculate the initial difference
        difference = math.fabs(pitches[1] - pitches[0])

        pos = -1

        ### Go through the pitches array and find the largest pitch change
        for i in range(pitches.size - 1):
            if (math.fabs(pitches[i + 1] - pitches[i])) > difference:
                difference = math.fabs(pitches[i + 1] - pitches[i])
                pos = i + 1

        ### If no pitch changes then append a placeholder time of 930 into the major pitch array
        if pos == -1:
            pass
            # future_major_pitch_array.append(930)
        else:
            # Else add pos*930 to the major pitch array
            pass
            # future_major_pitch_array.append(pos * 930)

    @staticmethod
    def major_volume_change(data_file_array):  # Work partially finished
        '''
        return position of biggest volume change in time in ms
        '''

        ### Get data of the file
        y, sr = data_file_array

        ### Get the initial difference
        difference = math.fabs(y[1] - y[0])

        pos = -1

        ### Go through the samples and find the largest amplitude (highest volume)
        for i in range(y.size - 1):
            if (math.fabs(y[i + 1] - y[i])) > difference:
                difference = math.fabs(y[i + 1] - y[i])
                pos = i + 1

        ### append into the major_volume_change_array rather than return the value
        ### future_major_volume_array.append((pos / (1161570 / 135)) * 1000)

    # Onset (major sound change) Detection (librosa has this exact function we can use)
    # return an array of onset appearances in time in ms
    # only works for monophonic sound (I think this means single channel sound)
    @staticmethod
    def onset_detection(data_file_array):
        """
        Output is an array of onsets (in seconds)
        Use librosa's onset detection function
        """

        ### Get data of the file
        y, sr = data_file_array

        ### Get the onsets of the file
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')

        ### Multiply the onsets to get it in seconds
        multiplied_onsets = onsets * 1000

        ### Return the onset array
        return multiplied_onsets

    @staticmethod
    def major_tempo_change(data_file_array):
        """
        Output is in ms
        Identify major tempo/beat change time
        return -1 if no beat change
        return location of biggest beat change
        Note that most songs could have the same beat throughout
        """

        ### Get data of the file
        y, sr = data_file_array

        ### Get the total tempo and beats using librosa
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        ### Convert the beats into times in seconds
        beat_times = librosa.frames_to_time(beats, sr=sr)

        ### Make beats become the beat_times
        beats = beat_times

        ### Get the initial difference
        difference = math.fabs(beats[1] - beats[0])

        pos = -1

        ### Get the position of the largest beat change
        for i in range(beats.size - 1):
            if (math.fabs(beats[i + 1] - beats[i])) > difference:
                difference = math.fabs(beats[i + 1] - beats[i])
                pos = i + 1

        ### If there is no beat changes then return pos (== -1 in that case)
        if (difference == math.fabs(beats[1] - beats[0])):
            return pos
        ### Else return the major beat change
        return beats[pos]


critical_time = Slicer.get_critical_time_index(max_duration=1, min_duration=3)
print(critical_time)
