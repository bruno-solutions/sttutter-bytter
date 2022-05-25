import ctypes

ReplayGain = ctypes.CDLL("audioprocess/lib/replaygain.dll")
ReplayGain.replaygain_test()
