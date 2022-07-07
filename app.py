"""The main module"""

import os

import pydub

import downloader
from audioprocess import AudioProcessor
from configuration import CACHE_WAV_FILE_NAME, CACHE_WEBM_FILE_NAME
from configuration import DEBUG_AUTO_CLEAN_CACHE
from configuration import URL, DURATION, THRESHOLD, SAMPLE_RATE, EXPORT_ROOT
from slicer import Slicer

tags = downloader.getsong(URL)

Slicer.invoke_slicers({"voice": "slice_at_voice"})

AudioProcessor(CACHE_WAV_FILE_NAME, SAMPLE_RATE) \
    .preprocess() \
    .apply_slicer(SAMPLE_RATE, DURATION if not None else 9, THRESHOLD if not None else 0.01, pydub.AudioSegment.voice, count=5) \
    .postprocess(tags, export_root=EXPORT_ROOT)

if DEBUG_AUTO_CLEAN_CACHE:
    os.remove(CACHE_WEBM_FILE_NAME)  # Depends on download.py if we convert it into webm or not
