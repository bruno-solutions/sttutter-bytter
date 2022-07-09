import math

from spleeter.audio.adapter import AudioAdapter
from spleeter.separator import Separator

from configuration import CACHE_WAV_FILE_NAME, DEFAULT_SAMPLE_RATE


class VoiceSlicer:
    """
    Slice source audio file using vocal cues
    """

    def __init__(self, sample_rate, duration, threshold):
        self.sample_rate = sample_rate
        self.duration = duration
        self.threshold = threshold
        self.stem_waveforms = None
        self.separator()

    def separator(self):
        """
        Use Spleeter to split the wav file into a dictionary of component amplitudes
        """
        separator = Separator('spleeter:2stems', multiprocess=False)
        audio_loader = AudioAdapter.default()
        waveform, _ = audio_loader.load(CACHE_WAV_FILE_NAME, sample_rate=DEFAULT_SAMPLE_RATE)
        self.stem_waveforms = separator.separate(waveform, CACHE_WAV_FILE_NAME)

    @staticmethod
    def get_var(duration, base_sample_index):
        """
        Return the needed variables for write_critical_time:
        end_sample_next_index: Starting at end_sample_index, get the next sample to see if it has a volume of 0
        add_time: How much time we go forward if we successfully get CTI's
        end_sample_starting_index: Where end_sample_index (the end-point for the CTI) will start
        end_sample_last_possible_index: The last possible sample index we can search till
        add_time_to_test_sample: If the initial base_sample_index value doesn't work, we go forward some samples with this variable
        """

        if 1 == duration:
            end_sample_next_index = 44100 // 4
            add_time = 44100 * 1
            end_sample_starting_index = base_sample_index + 44100 * duration - 44100 // 6
            end_sample_last_possible_index = base_sample_index + 44100
            add_time_to_test_sample = 44100 // 3
        elif 3 == duration:
            end_sample_next_index = 44100 // 4
            add_time = 44100 * 2
            end_sample_starting_index = base_sample_index + 44100 * duration - 44100 + 1
            end_sample_last_possible_index = base_sample_index + 44100 - 1
            add_time_to_test_sample = 44100 // 3
        elif 9 == duration:
            end_sample_next_index = 44100 // 4
            add_time = 44100 * 3
            end_sample_starting_index = base_sample_index + 44100 * duration - 44100 + 1
            end_sample_last_possible_index = base_sample_index + 44100 - 1
            add_time_to_test_sample = 44100 // 4
        elif 27 == duration:
            end_sample_next_index = 44100 // 4
            add_time = 44100 * 3
            end_sample_starting_index = base_sample_index + 44100 * duration - 44100 + 1
            end_sample_last_possible_index = base_sample_index + 44100 - 1
            add_time_to_test_sample = 44100 // 4
        else:
            raise ValueError("Wrong time input. It must be either 1, 3, 9, or 27 seconds!")

        return end_sample_next_index, add_time, end_sample_starting_index, end_sample_last_possible_index, add_time_to_test_sample

    def write_critical_time(self, cti):
        """
        Adds critical time indexes to the passed CTI array using Spleeter's vocal seperation function dictionary component cues
        Input: CTI array to which to append voice cued CTIs
        """
        total_samples = self.stem_waveforms['vocals'].shape[0]
        base_sample_index = 0

        while not base_sample_index > total_samples:
            end_sample_next_index, add_time, end_sample_starting_index, end_sample_last_possible_index, add_time_to_test_sample = self.get_var(self.duration, base_sample_index)

            if math.fabs(self.stem_waveforms['vocals'][base_sample_index][0]) <= self.threshold:
                if base_sample_index + self.sample_rate * self.duration + self.sample_rate // 2 <= total_samples:
                    end_sample_index = end_sample_starting_index  # to use as starting point for end_sample_index
                else:
                    break

                # When the current volume is 0 then search for a 0 volume by adding time parameter to current time position
                while self.stem_waveforms['vocals'][end_sample_index][0] != self.stem_waveforms['vocals'][end_sample_last_possible_index][0]:
                    if self.stem_waveforms['vocals'][end_sample_index][0] <= self.threshold:
                        cti.append([base_sample_index / self.sample_rate * 1000, end_sample_index / self.sample_rate * 1000])
                        break
                    else:
                        # Go forward some samples from end_sample_index to test again for a 0 volume
                        end_sample_index += end_sample_next_index
                base_sample_index += add_time
            else:
                # From base_sample_index go forward some samples to get to next value to test for a 0 volume
                base_sample_index += add_time_to_test_sample
