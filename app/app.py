"""The main module"""

import os

import pydub

import downloader
from audioprocessor import AudioProcessor
from configuration import CACHE_WAV_FILE_NAME, CACHE_WEBM_FILE_NAME
from configuration import URL, DURATION, THRESHOLD, DEFAULT_SAMPLE_RATE, EXPORT_ROOT
from slicer import Slicer

tagger = downloader.get_song_aria2c(URL)

slicers = {"voice": "slice_at_voice"}

Slicer.register(slicers, tagger)

AudioProcessor(CACHE_WAV_FILE_NAME, DEFAULT_SAMPLE_RATE, tagger) \
    .preprocess() \
    .slice(DEFAULT_SAMPLE_RATE, DURATION if not None else 9, THRESHOLD if not None else 0.01, pydub.AudioSegment.voice, count=5) \
    .postprocess() \
    .export(directory=EXPORT_ROOT)

try:
    os.remove(CACHE_WEBM_FILE_NAME)
except OSError:
    pass
