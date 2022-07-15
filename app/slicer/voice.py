from typing import List

import numpy
import pydub
from spleeter.separator import Separator

from configuration import LOG_DEBUG, TEMP_VOICE_FILE_NAME, AUDIO_FILE_TYPE
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

        # TODO Consider running the source file through Spleeter multiple times
        # TODO Consider wav subtraction of other stems

        # https://github.com/deezer/spleeter

        samples = recording.get_array_of_samples()  # 19,535,872 (int16) = 39,071,744 bytes
        samples_reshaped = numpy.reshape(samples, (-1, recording.channels))  # 9,767,936 (int16) * 2 = 19,535,872 (int) = 39,071,744 bytes
        vocals = Separator('spleeter:2stems', multiprocess=False).separate(samples_reshaped)['vocals']  # 9,767,936 (float) * 2 = 19,535,872 (float) = 78,143,488 bytes
        vocals_as_int = numpy.array(vocals, dtype=numpy.int16)  # 9,767,936 (int16) * 2 = 19,535,872 (int) = 39,071,744 bytes
        vocals_as_int_reshaped = numpy.reshape(vocals_as_int, (recording.channels, -1))  # 2 * 9,767,936 (int) = 19,535,872 (int) = 39,071,744 bytes
        as_bytes = vocals_as_int_reshaped.tobytes()  # 39,071,744 bytes
        vocal_recording = pydub.AudioSegment(data=as_bytes, frame_rate=recording.frame_rate, sample_width=recording.sample_width, channels=recording.channels)

        if LOG_DEBUG:
            vocal_recording.export(out_f=TEMP_VOICE_FILE_NAME, format=AUDIO_FILE_TYPE).close()

        volume_slicer = VolumeSlicer(vocal_recording, detection_chunk_size_miliseconds, low_volume_threshold_decibels, volume_drift_decibels, max_clips)

        self.sci: List[SampleClippingInterval] = volume_slicer.get()

    def get(self):
        return self.sci
