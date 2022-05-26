from email.mime import audio
from email.utils import format_datetime
from typing_extensions import Self
from pydub import AudioSegment

import array
import ffmpeg
import os
import json
import librosa
#import requests

#Get Leveled AudioFile
def getLeveledAudioFile():
    #From downloader file
    #name = stWavFile.wav
    return AudioSegment.from_file("stWavFile.wav", format="wav")

#pydub(fade in/ fade out)
#input: a list of clips will be processed, which is decided by user
def processAudioClip(target):
    pass

#input:
#   start: start time of audio
#   end: end time of audio
#return: a AudioSegment file
def cutAudioHelper(start, end):##TESTNEEDED
    #file audio temp is exist
    audio.export("audioTemp\\temp.wav", format = "wav")
    return AudioSegment.from_file("audioTemp\\temp.wav", format="wav") [start: end]


#Another helper of cutAudio method
def AudioClipsNameRoller():
    i = 0
    while True:
        yield i
        i += 1

#input: List of pair of critical times
#output: push all clips to AllAudioClips file.
def cutAudio(criticalTime):
    if not os.path.exists("AllAudioClips"):
        os.makedirs("AllAudioClips")
    name = AudioClipsNameRoller()
    for pair in criticalTime:
        cutAudioHelper(pair[0], pair[1]).export("AllAudioClips\\" + str(next(name)) + ".wav", format="wav")

#Lyrics(Shazam/MusicMixer(testing))
#DrumSetChange/beatChage(librosa/AudioOwl)
#pitchChange(librosa/AudioOwl)
#reuturn: a list of pair list of critical times in ms
#   e.g: [[star1, end1],[star2, end2], [star3, end3]...]
#we could mix match difference major change in pitch, beat, volumne to create more ways of slicing (like they can be different start, end points)
def getCriticalTimeIndex():
    pass

#Return a list of                                                                                                                                                                               time that lyrics emerge or disappear
def getLyricsChangeTimes():
    pass

#Identify major pitch change time
#search pitch detection algorithm (PDA)
#https://librosa.org/doc/latest/core.html (librosa pitch detection)
def majorPitchChange():
    pass

#Identify major volumn change time
def majorVolumnChange():
    pass

#Onset (major sound change) Detection (librosa has this exact functin we can use)
#return an array of onset appearances in time
#only works for monophonic sound
def onsetDetection():
    y, sr = librosa.load#(filename)
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    return onsets

#Identify major tempo/beat change time
#return -1 if no beat change
#return location of biggest beat change
#Note that most songs could have the same beat throughout
def majorTempoChange():
    y, sr = librosa.load#(filename)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    beats=beat_times
    difference=0
    pos=-1
    for i in range(beats.len()-1):
        if (beats[i+1]-beats[i])>difference:
            difference = beats[i+1]-beats[i]
            pos = i+1
    if (difference==beats[1]-beats[0]):
        return -1
    return beats[pos]


#push out all audio clip into output file with {certain} formmat
def pushOutClips():
    pass

#MAIN
if not os.path.exists("audioTemp"):
    os.mkdir("audioTemp")

audio = getLeveledAudioFile()
processAudioClip()
