"""The main module"""

import os
import pydub

import downloader
from audioprocess import AudioProcessor
from slicer import Slicer

DEBUG_AUTO_CLEAN_CACHE = False

# The sample rate for the wav file
SAMPLE_RATE = 44100  # Todo: Allow files to be processed of any sample rate

downloader.getsong("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

Slicer.invoke_slicers({
    "voice": "slice_at_voice"
})

AudioProcessor("cache/ytdl-fullsong.wav") \
    .preprocess() \
    .apply_slicer(
    SAMPLE_RATE,
    pydub.AudioSegment.voice,  # pylint: disable=no-member
    count=5  # since all slicer members are dynamically loaded.
) \
    .postprocess(
    export_path="./cache/test_export"
)

if DEBUG_AUTO_CLEAN_CACHE:
    # Depends on download.py if we convert it into webm or not
    os.remove("cache/ytdl-fullsong.webm")

