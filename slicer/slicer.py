import array
import re
from unittest import result
import ffmpeg
import os
import json
import librosa
import math
import numpy as np
#import requests

from email.mime import audio
from email.utils import format_datetime
from typing_extensions import Self
from pydub import AudioSegment


def getLeveledAudioFile():
    """Get Leveled AudioFile"""

    #From downloader file
    #name = stWavFile.wav
    return AudioSegment.from_file("stWavFile.wav", format="wav")

def processAudioClip(ClipList):
    """
    pydub(fade in/ fade out)
    input: a list of clips will be processed
    """

    for clip in ClipList:
        clip.fade_in(250)
        clip.fade_out(250)

def getCopyOfAudio(target):
    """"
    Since the audio change will fundmentally change the original file,
    this method is help to get a copy of original file.
    """

    #file audioTemp is exist from main function
    target.export("audioTemp\\temp.wav", format = "wav")
    re = AudioSegment.from_file("audioTemp\\temp.wav", format="wav")
    os.remove("audioTemp\\temp.wav")
    return re

def cutAudio(criticalTime, target):
    """
    input: List of pair of critical times
    output: push all clips to AllAudioClips file.
    """
    re = []
    for pair in criticalTime:
        re.append(getCopyOfAudio(target)[pair[0]: pair[1]])
    return re


def pushOutClips(audioList):
    """
    input: an array of cutted audioSegment Objects
    push out all audio clip into output file with {certain} formmat
    """

    if not os.path.exists("AllAudioClips"):
        os.makedirs("AllAudioClips")
    name = AudioClipsNameRoller()
    for Segment in audioList:
        Segment.export("AllAudioClips\\" + str(next(name)) + ".wav", format="wav")


def AudioClipsNameRoller():
    """A naming helper of pushOutClips()"""
    
    i = 0
    while True:
        yield i
        i += 1
        
#Lyrics(Shazam/MusicMixer(testing))
#DrumSetChange/beatChage(librosa/AudioOwl)
#pitchChange(librosa/AudioOwl)
#reuturn: a list of pair list of critical times in ms
#   e.g: [[star1, end1],[star2, end2], [star3, end3]...]
#We could mix match difference major change in pitch, beat, volumne to create more ways of slicing (like they can be different start, end points)
def getCriticalTimeIndex():
    """#reuturn: a list of pair list of critical times in ms
    e.g: [[star1, end1],[star2, end2], [star3, end3]...]
    """
    pass

#Return a list of                                                                                                                                                                               time that lyrics emerge or disappear
def getLyricsChangeTimes():
    pass

#Output is in ms
#Identify major pitch change time
#search pitch detection algorithm (PDA)
#Note: If multi-channel input is provided, frequency curves are estimated separately for each channel
#So to prevent error, we might need to pass in single channel input
def majorPitchChange():
    y, sr = librosa.load#(filename)
    pitches = librosa.yin(y, fmin=65, fmax=2093, frame_length=20480)
    difference = math.fabs(pitches[1]-pitches[0])
    pos = -1
    for i in range(pitches.len()-1):
        if (math.fabs(pitches[i+1]-pitches[i]))>difference:
            difference = math.fabs(pitches[i+1]-pitches[i])
            pos = i+1
    if (pos == -1):
        return 930
    time = pos*930
    return  time

#Identify major volumn change time
#Work in progress
def majorVolumnChange():
    y, sr = librosa.load#(filename)
    S = np.abs(librosa.stft(y))
    pass

#Onset (major sound change) Detection (librosa has this exact functin we can use)
#return an array of onset appearances in time in ms
#only works for monophonic sound (I think this means single channel sound)
def onsetDetection():
    y, sr = librosa.load#(filename)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    multiplied_onsets = onsets*1000
    return multiplied_onsets

#Output is in ms
#Identify major tempo/beat change time
#return -1 if no beat change
#return location of biggest beat change
#Note that most songs could have the same beat throughout
def majorTempoChange():
    y, sr = librosa.load#(filename)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    beats=beat_times
    difference = math.fabs(beats[1]-beats[0])
    pos=-1
    for i in range(beats.len()-1):
        if (math.fabs(beats[i+1]-beats[i]))>difference:
            difference = math.fabs(beats[i+1]-beats[i])
            pos = i+1
    if (difference == math.fabs(beats[1]-beats[0])):
        return -1
    return beats[pos]*1000

#MAIN
if not os.path.exists("./audioTemp"):
    os.mkdir("audioTemp")
