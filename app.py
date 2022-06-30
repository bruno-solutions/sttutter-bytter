"""The main module"""

import os

import pydub

import downloader
from audioprocess import AudioProcessor
from configuration import DEBUG_AUTO_CLEAN_CACHE, DURATION, THRESHOLD, SAMPLE_RATE, CACHE_WAV_FILE_NAME, CACHE_WEBM_FILE_NAME, URL
from slicer import Slicer

downloader.getsong("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

Slicer.invoke_slicers({"voice": "slice_at_voice"})

AudioProcessor(CACHE_WAV_FILE_NAME, SAMPLE_RATE) \
    .preprocess() \
    .apply_slicer(SAMPLE_RATE, DURATION if not None else 9, THRESHOLD if not None else 0.01, pydub.AudioSegment.voice, count=5) \
    .postprocess(export_path="./cache/test_export")

if DEBUG_AUTO_CLEAN_CACHE:
    os.remove(CACHE_WEBM_FILE_NAME)  # Depends on download.py if we convert it into webm or not
