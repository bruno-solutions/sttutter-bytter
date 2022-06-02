"""A module used only for testing."""

import os
import pydub

import downloader
from audioprocess import AudioProcessor
from slicer import Slicer


DEBUG_AUTO_CLEAN_CACHE = False


# downloader.getsong("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Slicer.invoke_slicers({
#     "temporary_test_mode": "random_slice"
# })

# AudioProcessor()\
#     .preprocess()\
#     .apply_slicer(
#         pydub.AudioSegment.temporary_test_mode, # pylint: disable=no-member
#         count=5                                 # since all slicer members are dynamically loaded.
#     )\
#     .postprocess(
#         export_path="./cache/test_export"
#     )

# if DEBUG_AUTO_CLEAN_CACHE:
#     os.remove("cache/ytdl-fullsong.webm")
