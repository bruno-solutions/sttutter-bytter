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


import numpy
import librosa

ldata = librosa.load("./cache/ytdl-fullsong.webm", sr=None)[0]
pdata_raw = numpy.array(pydub.AudioSegment.from_file("./cache/ytdl-fullsong.webm").get_array_of_samples())

pdata_l = pdata_raw[::2]
pdata_r = pdata_raw[1::2]

pdata = (pdata_l+pdata_r)/2

pdata_conv = pdata/numpy.iinfo(numpy.int32).max

print(ldata[150040:150050])
print(pdata_conv[150040:150050])

pass
