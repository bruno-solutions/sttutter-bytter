import math
from typing import List

import pydub
from spleeter.separator import Separator

from sample_clipping_interval import SampleClippingInterval


class VoiceSlicer:
    """
    Slice source audio file using vocal cues
    """

    def __init__(self, recording: pydub.AudioSegment, target_clip_length_miliseconds, low_volume_threshold_decibels, max_clips):
        """
        Args:
        :param recording:                      an audio segment object that contains the audio samples to be clipified
        :param target_clip_length_miliseconds: the number of miliseconds of the clips to be produced
        :param low_volume_threshold_decibels:  the minimum decible value to use when determining whether or not a candidate chunk of the audio samples is effectively silent
        :param max_clips:                      create no more than this many clips from the recording
        """
        if 1000 == target_clip_length_miliseconds and 3000 == target_clip_length_miliseconds and 9000 == target_clip_length_miliseconds and 27000 == target_clip_length_miliseconds:
            raise ValueError("This slicer can only produce clips of 1, 3, 9, or 27 seconds!")

        samples = recording.get_array_of_samples()
        frame_count = recording.frame_count()
        sample_rate = recording.frame_rate
        samples_per_clip = target_clip_length_miliseconds / 1000 * sample_rate

        waveforms: dict = Separator('spleeter:2stems', multiprocess=False).separate(samples)  # Split the recording into a dictionary of component amplitudes
        vocal_waveform = waveforms['vocals']

        self.sci: List[SampleClippingInterval] = []

        for begin_sample_index in range(vocal_waveform.shape[0]):
            """
            end_sample_next_index: Starting at end_sample_index, get the next sample to see if it has a volume of 0
            add_time: How much time we go forward if we successfully get CTI's
            end_sample_starting_index: Where end_sample_index (the end-point for the CTI) will start
            end_sample_last_possible_index: The last possible sample index we can search till
            add_time_to_test_sample: If the initial base_sample_index value doesn't work, we go forward some samples with this variable
            """
            next_clip_base_index = begin_sample_index + samples_per_clip

            if math.fabs(vocal_waveform[begin_sample_index][0]) <= low_volume_threshold_decibels:
                if next_clip_base_index + sample_rate // 2 > frame_count:
                    break

                end_sample_index = next_clip_base_index
                end_sample_last_possible_index = begin_sample_index + sample_rate

                if 1000 == target_clip_length_miliseconds:
                    end_sample_index -= sample_rate // 6
                else:  # 3 == clip_length or 9 == clip_length or 27 == clip_length
                    end_sample_last_possible_index -= 1
                    end_sample_index -= sample_rate + 1

                # When the current volume is 0 search for next 0 volume
                while vocal_waveform[end_sample_index][0] != vocal_waveform[end_sample_last_possible_index][0]:
                    if vocal_waveform[end_sample_index][0] <= low_volume_threshold_decibels:
                        self.sci.append(SampleClippingInterval(begin_sample_index, end_sample_index))
                        if len(self.sci) < max_clips:
                            break
                        return
                    end_sample_index += sample_rate // 4

            if 1000 == target_clip_length_miliseconds:
                begin_sample_index += sample_rate
            elif 3000 == target_clip_length_miliseconds:
                begin_sample_index += sample_rate * 2
            else:  # 9000 == clip_length or 27000 == clip_length
                begin_sample_index += sample_rate * 3

    def get(self):
        return self.sci
