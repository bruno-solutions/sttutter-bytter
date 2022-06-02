"""Provide math func support"""
from base64 import standard_b64encode
import math
import os

import librosa
import numpy as np
from pydub import AudioSegment
from sklearn.multiclass import OneVsRestClassifier

#MAIN
if not os.path.exists("./audioTemp"):
    os.mkdir("audioTemp")

class Slicer:
    """
    Slicer
    """
    def __init__(self, file):
        self.y, self.sr = librosa.load(file)

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
        def name_roller():
            i = 0
            while True:
                yield i
                i += 1
        name = name_roller()
        for segment in clip_list:
            segment.export("AllAudioClips\\" + str(next(name)) + ".wav", format="wav")

    # def name_roller(self):
    #     """A naming helper of push_out_clips()"""
    #     i = 0
    #     while True:
    #         yield i
    #         i += 1

    #Lyrics(Shazam/MusicMixer(testing))
    #DrumSetChange/beatChage(librosa/AudioOwl)
    #pitchChange(librosa/AudioOwl)
    #We could mix match difference major change in pitch, beat, volumne to create more ways of slicing (like they can be different start, end points)
    def get_critical_time_index(self, max_duration, min_duration, clips_nums=1):
        """
        input:
            max_duration: Maximun time duration of a single clips
            min_duration: Minmun time duration of a single clips
            clips_nums: number of clips will be returned. Default @ 1
            reuturn: a list of pair list of critical times in ms
        e.g: [[star1, end1],[star2, end2], [star3, end3]...]
        """
        #standard_duration = #8bars 32*BPM

        # Questions:
        #   1. What is the basic part of music?
        #   2. What if the clips is repeated?
        #   3. How can we decide which part is most valuable part?
        
        #overlay two array to find most strike point
        #intersection(l1,l2)

    def intersect(self, list1, list2):
        list3 = [value for value in list1 if value + 50]
    #course/verse detection by time space between human voice
    #cut in space
    #

    # def get_percussive_times(self):
    #     pass

    # #waiting for Shazam API
    # def get_lyrics_change_times(self):
    #     pass

    
    def major_pitch_change(self):
        """
        Output is in ms
        Identify major pitch change time
        search pitch detection algorithm (PDA)
        Note:
            If multi-channel input is provided,
            frequency curves are estimated separately for each channel,
            so to prevent error, we might need to pass in single channel input
        """

        pitches = librosa.yin(self.y,fmin=40, fmax=2200, sr=22050, frame_length=2048)
        difference = math.fabs(pitches[2]-pitches[1])
        pos = -1
        for i in range(1, pitches.size-1):
            if (math.fabs(pitches[i+1]-pitches[i]))>difference:
                difference = math.fabs(pitches[i+1]-pitches[i])
                pos = i+1
        if pos == -1:
            return 4/173
        else:
            return pos * (4/173)

    def major_volumn_change(self):#Work partially finished
        '''
        return position of biggest volumn change in time in ms
        '''
        y, sr = librosa.load('80HZVolum2.wav')#sr=22050)
        return y, sr ##### here slicer\\slicerTestSrc\\80HZVolum2.wav

        difference = math.fabs(self.y[1]-self.y[0])
        pos=-1
        for i in range(self.y.size-1):
            if (math.fabs(self.y[i+1]-self.y[i])) > difference:
                difference = math.fabs(self.y[i+1]-self.y[i])
                pos = i+1
            return (pos/(1429038/60))*1000

    
    def onset_detection(self):
        """
        Onset (major sound change) Detection (librosa has this exact function we can use)
        return an numpy array of onset appearances in time in ms
        only works for monophonic sound (I think this means single channel sound)
        """
        return librosa.onset.onset_detect(y = self.y, sr = self.sr, units ='time')
        #multiplied_onsets = onsets*1000
        #return multiplied_onsets

    def get_real_time_tempo(self):
        onset_env = librosa.onset.onset_strength(y=self.y,sr=self.sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env,sr=self.sr,aggregate=None)
        return tempo
        
    
    def major_tempo_change(self):
         """
         Output is in ms
         Identify major tempo (beats per minute) change time
         return -1 if no tempo change
         return location of biggest tempo change
         Note that most songs could have the same tempo throughout
         """
         onset_env = librosa.onset.onset_strength(y=self.y,sr=self.sr)
         tempo = librosa.beat.tempo(onset_envelope=onset_env,sr=self.sr,aggregate=None)

         difference = math.fabs(tempo[1]-tempo[0])

         pos=-1
         for i in range(tempo.size-1):
             if (math.fabs(tempo[i+1]-tempo[i])) >= difference+2:
                 difference = math.fabs(tempo[i+1]-tempo[i])
                 pos = i+1
         if difference == math.fabs(tempo[1]-tempo[0]):
             return -1

         time_from_frame = librosa.frames_to_time(pos, sr=self.sr)
         return time_from_frame

    def get_tempo(self):
        tempo, beats = librosa.beat.beat_track(y = self.y, sr = self.sr)
        return tempo
    
    def get_beat_time(self):
        tempo, beats = librosa.beat.beat_track(y = self.y, sr = self.sr)
        return librosa.frames_to_time(beats, sr=self.sr)

    def get_pitch(self):
        return librosa.yin(self.y,fmin=440, fmax=880, sr=22050, frame_length=2048)

    def get_amplitude(self):
        return self.y

    def get_volume(self):
        return librosa.amplitude_to_db(S=self.y,ref=0)

    #bpm higher-> freedom down
    #freedom constant
    def highlighter(self, onset, beats):
        re = []
        #cur_pointer = 0
        for b in beats:
            for o in onset:
                if math.fabs(b - o) < 0.0348: #free = 3.1008 / bpm #60 / bpm
                    re.append(b)
                    #break
        return re
    
    def highlighter2(self, onset, beats):
        re = []
        #cur_pointer = 0
        for b in beats:
            for o in onset:
                if b == o:
                    re.append(b)
                    #break
        return re

    #barDuration(bpm) = 4/ 60 / bpm / (s/ bar)
        #bpm(beat/min) 4(beats/bar) 60(s)
    #s/bar 240/bpm
    #0.5s for faded out


s=Slicer("test_data\\test_cases\\tempo test 3.wav")

print("beat at time:")
print(s.get_beat_time())
print("tempo:")
print(s.get_tempo())
print("tempo change at time:")
print(s.major_tempo_change())


