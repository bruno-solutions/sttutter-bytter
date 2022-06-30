"""The main module"""

import os

import pydub

import downloader
from audioprocess import AudioProcessor
from slicer import Slicer

DEBUG_AUTO_CLEAN_CACHE = False
DEBUG_LOAD_WAV_ONLY = True

DURATION = 3
THRESHOLD = 0.01
SAMPLE_RATE = 44100  # Todo: Allow files to be processed of any sample rate (currently set to 44100 in downloader)

downloader.getsong("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

Slicer.invoke_slicers({"voice": "slice_at_voice"})

AudioProcessor(SAMPLE_RATE, "cache/ytdl-fullsong.wav", DEBUG_LOAD_WAV_ONLY) \
    .preprocess() \
    .apply_slicer(SAMPLE_RATE, DURATION if not None else 9, THRESHOLD if not None else 0.01, pydub.AudioSegment.voice, count=5) \
    .postprocess(export_path="./cache/test_export")

if DEBUG_AUTO_CLEAN_CACHE:
    os.remove("cache/ytdl-fullsong.webm")  # Depends on download.py if we convert it into webm or not
