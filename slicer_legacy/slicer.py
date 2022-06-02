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

#import requests
#MAIN
if not os.path.exists("./audioTemp"):
    os.mkdir("audioTemp")

class Slicer:
    """
    Slicer
    """
    def __init__(self):
        pass

    #unfunished since Leveling function is not finished
    @staticmethod
    def get_leveled_audio_file():
        """
        Get Leveled AudioFile
        return a AudioSegment object
        """
        #From downloader file
        #name = stWavFile.wav
        return AudioSegment.from_file("stWavFile.wav", format="wav")

    @staticmethod
    def process_audio_clip(clip_list):
        """
        pydub(fade in/ fade out)
        input: a list of clips will be processed
        """
        for clip in clip_list:
            clip.fade_in(250)
            clip.fade_out(250)

    @staticmethod
    def get_copy_of_audio(target):
        """"
        Since the audio change will fundmentally change the original file,
        this method is help to get a copy of original file.
        """

        #file audioTemp is exist from main function
        target.export("audioTemp\\temp.wav", format = "wav")
        re = AudioSegment.from_file("audioTemp\\temp.wav", format="wav")
        os.remove("audioTemp\\temp.wav")
        return re

    @staticmethod
    def cut_audio(critical_time, target):
        """
        input: List of pair of critical times
        output: push all clips to AllAudioClips file.
        """
        re = []
        for pair in critical_time:
            re.append(Slicer.get_copy_of_audio(target)[pair[0]: pair[1]])
        return re

    @staticmethod
    def push_out_clips(clip_list):
        """
        input: an array of cutted audioSegment Objects
        push out all audio clip into output file with {certain} formmat
        """

        if not os.path.exists("AllAudioClips"):
            os.makedirs("AllAudioClips")
        name = Slicer.name_roller()
        for segment in clip_list:
            segment.export("AllAudioClips\\" + str(next(name)) + ".wav", format="wav")

    @staticmethod
    def name_roller():
        """A naming helper of push_out_clips()"""
        i = 0
        while True:
            yield i
            i += 1

    #Lyrics(Shazam/MusicMixer(testing))
    #DrumSetChange/beatChage(librosa/AudioOwl)
    #pitchChange(librosa/AudioOwl)
    #We could mix match difference major change in pitch, beat, volumne to create more ways of slicing (like they can be different start, end points)
    @staticmethod
    def get_critical_time_index(max_duration, min_duration, clips_nums=1):
        """
        input:
            max_duration: Maximun time duration of a single clips
            min_duration: Minmun time duration of a single clips
            clips_nums: number of clips will be returned. Default @ 1
        reuturn: a list of pair list of critical times in ms
        e.g: [[star1, end1],[star2, end2], [star3, end3]...]
        """
        #sample code, work as place holder
        temp = [
                Slicer.major_volumn_change(),
                Slicer.major_tempo_change(),
                # Slicer.major_pitch_change()
                ]
        for i in Slicer.onset_detection():
            temp.append(i)
        re = []
        for i in range(int(len(temp)/2)):
            re.append([temp[i*2],temp[i*2+1]])
        return re

    @staticmethod
    def get_lyrics_change_times():
        pass

    @staticmethod
    def major_pitch_change(data_array):
        """
        Output is in ms
        Identify major pitch change time
        search pitch detection algorithm (PDA)
        Note: 
            If multi-channel input is provided, frequency curves are estimated separately for each channel
            So to prevent error, we might need to pass in single channel input
        """
        y, sr = librosa.load(librosa.ex('trumpet')) ###all files are currenly librosa example files, used as placeholder
        pitches = librosa.yin(y, fmin=65, fmax=2093, frame_length=20480)
        difference = math.fabs(pitches[1]-pitches[0])
        pos = -1
        for i in range(pitches.size-1):
            if (math.fabs(pitches[i+1]-pitches[i]))>difference:
                difference = math.fabs(pitches[i+1]-pitches[i])
                pos = i+1
        if (pos == -1):
            return 930
        else:
            return pos * 930

    @staticmethod
    def major_volumn_change():#Work partially finished
        '''
        return position of biggest volumn change in time in ms
        '''
        y, sr = librosa.load(librosa.ex('trumpet'),)#sr=22050)
        #return y, sr

        difference = math.fabs(y[1]-y[0])
        pos=-1
        for i in range(y.size-1):
            if (math.fabs(y[i+1]-y[i]))>difference:
                difference = math.fabs(y[i+1]-y[i])
                pos = i+1
            return (pos/(1161570/135))*1000

    #Onset (major sound change) Detection (librosa has this exact function we can use)
    #return an array of onset appearances in time in ms
    #only works for monophonic sound (I think this means single channel sound)
    @staticmethod
    def onset_detection():
        y, sr = librosa.load(librosa.ex('trumpet'))
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
        multiplied_onsets = onsets*1000
        return multiplied_onsets

    @staticmethod
    def major_tempo_change():
        """
        Output is in ms
        Identify major tempo/beat change time
        return -1 if no beat change
        return location of biggest beat change
        Note that most songs could have the same beat throughout
        """

        y, sr = librosa.load(librosa.ex('trumpet'))
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        beats=beat_times
        difference = math.fabs(beats[1]-beats[0])
        pos=-1
        for i in range(beats.size-1):
            if (math.fabs(beats[i+1]-beats[i]))>difference:
                difference = math.fabs(beats[i+1]-beats[i])
                pos = i+1
        if (difference == math.fabs(beats[1]-beats[0])):
            return -1
        return beats[pos]*1000

critical_time = Slicer.get_critical_time_index(max_duration=1, min_duration=3)
print(critical_time)
