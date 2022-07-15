from typing import List

import numpy
import pydub
from spleeter.separator import Separator

from configuration import TEMP_ROOT
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
        temp_voice_file_name = f"{TEMP_ROOT}\\vocal.wav"

        # https://github.com/deezer/spleeter

        samples = recording.get_array_of_samples()  # 19,535,872 (int16) = 39,071,744 bytes
        array = numpy.reshape(samples, (-1, recording.channels))  # 9,767,936 (int16) * 2 = 19,535,872 (int) = 39,071,744 bytes
        vocals = Separator('spleeter:2stems', multiprocess=False).separate(array)['vocals']  # 9,767,936 (float) * 2 = 19,535,872 (float) = 78,143,488 bytes
        vocals_as_int = numpy.array(vocals, dtype=numpy.int16)  # 9,767,936 (int16) * 2 = 19,535,872 (int) = 39,071,744 bytes
        vocals_as_int_reshaped = numpy.reshape(vocals_as_int, (recording.channels, -1))  # 2 * 9,767,936 (int) = 19,535,872 (int) = 39,071,744 bytes
        as_bytes = vocals_as_int_reshaped.tobytes()  # 39,071,744 bytes
        vocal_recording = pydub.AudioSegment(data=as_bytes, frame_rate=recording.frame_rate, sample_width=recording.sample_width, channels=recording.channels)
        vocal_recording.export(out_f=temp_voice_file_name, format="wav").close()
        vocal_recording = pydub.AudioSegment.from_file(temp_voice_file_name)
        volume_slicer = VolumeSlicer(vocal_recording, detection_chunk_size_miliseconds, low_volume_threshold_decibels, volume_drift_decibels, max_clips)

        self.sci: List[SampleClippingInterval] = volume_slicer.get()

    def get(self):
        return self.sci
