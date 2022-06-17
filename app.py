"""The main module"""

import os
import pydub

import downloader
from audioprocess import AudioProcessor
from slicer import Slicer

DEBUG_AUTO_CLEAN_CACHE = False

downloader.getsong("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

Slicer.invoke_slicers({
    "beats": "generate_from_beats"
})

# Zach's test case
# AudioProcessor("./test_data/test_cases/loudness_change_at_2sec.wav") \
# Rohan's test case
AudioProcessor("cache/ytdl-fullsong.wav") \
    .preprocess() \
    .apply_slicer(
    pydub.AudioSegment.beats,  # pylint: disable=no-member
    count=5  # since all slicer members are dynamically loaded.
) \
    .postprocess(
    export_path="./cache/test_export"
)

if DEBUG_AUTO_CLEAN_CACHE:
    # Depends on download.py if we convert it into webm or not
    os.remove("cache/ytdl-fullsong.webm")

