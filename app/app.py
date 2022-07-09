"""The main module"""

import os
import shutil

import pydub

import downloader
from audioprocessor import AudioProcessor
from configuration import CACHE_ROOT, CACHE_WAV_FILE_NAME
from configuration import URL, DURATION, THRESHOLD, DEFAULT_SAMPLE_RATE, EXPORT_ROOT
from slicer import Slicer


def purge_files():
    cache_root = f"{os.getcwd()}\\{CACHE_ROOT}"
    export_root = f"{os.getcwd()}\\{EXPORT_ROOT}"

    try:
        shutil.rmtree(cache_root)
    except FileNotFoundError:
        print(f"[NOTICE]: {cache_root} directory does not exist (but that's OK, I'll make it for you)")
        pass

    try:
        shutil.rmtree(export_root)
    except FileNotFoundError:
        print(f"[NOTICE]: {export_root} directory does not exist (but that's OK, I'll make it for you)")
        pass


purge_files()

tagger = downloader.get_song_aria2c(URL)

slicers = {"voice": "slice_at_voice"}

Slicer.register(slicers, tagger)

AudioProcessor(CACHE_WAV_FILE_NAME, DEFAULT_SAMPLE_RATE, tagger) \
    .preprocess() \
    .slice(DEFAULT_SAMPLE_RATE, DURATION if not None else 9, THRESHOLD if not None else 0.01, pydub.AudioSegment.voice, count=5) \
    .postprocess() \
    .export(directory=EXPORT_ROOT)
