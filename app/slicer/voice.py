from typing import List

import pydub
from spleeter.separator import Separator

from sample_clipping_interval import SampleClippingInterval
from volume import VolumeSlicer


class VoiceSlicer:
    """
    Slice source audio recording using vocal cues
    """

    def __init__(self, recording: pydub.AudioSegment, detection_chunk_size_miliseconds: int, low_volume_threshold_decibels: int, volume_drift_decibels: int, max_clips: int):
        """
        Args:
        :param recording:                        an audio segment object that contains the audio samples to be processed
        :param detection_chunk_size_miliseconds: the number of samples of the recording to analyze per chunk
        :param low_volume_threshold_decibels:    the minimum decible value to use when determining the peak volume of a chunk
        :param volume_drift_decibels:            the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        :param max_clips:                        create no more than this many clips from the recording
        """
        waveforms: dict = Separator('spleeter:2stems', multiprocess=False).separate(recording.get_array_of_samples())
        vocal_recording = pydub.AudioSegment(data=waveforms['vocals'], frame_rate=recording.frame_rate, frame_width=recording.frame_width, channels=recording.channels)
        volume_slicer = VolumeSlicer(vocal_recording, detection_chunk_size_miliseconds, low_volume_threshold_decibels, volume_drift_decibels, max_clips)

        self.sci: List[SampleClippingInterval] = volume_slicer.get()

    def get(self):
        return self.sci
