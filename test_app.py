"""A module used only for testing."""

import os
import pydub

import downloader
from audioprocess import AudioProcessor
from slicer import Slicer


DEBUG_AUTO_CLEAN_CACHE = False


# downloader.getsong("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

Slicer.invoke_slicers({
    "volumeSlicer": "slice_at_volume_change"
})

AudioProcessor("./test_data/test_cases/loudness_change_at_2sec.wav")\
    .preprocess()\
    .apply_slicer(
        pydub.AudioSegment.volumeSlicer, # pylint: disable=no-member
        count=5                          # since all slicer members are dynamically loaded.
    )\
    .postprocess(
        export_path="./cache/test_export"
    )

if DEBUG_AUTO_CLEAN_CACHE:
    os.remove("cache/ytdl-fullsong.webm")
