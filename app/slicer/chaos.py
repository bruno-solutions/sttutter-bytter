import random
from typing import List

import pydub

from sample_clipping_interval import SampleClippingInterval


class ChaosSlicer:
    """
    Random interval slicer
    """

    def __init__(self, recording: pydub.AudioSegment, max_clips=10, pad_miliseconds=250):
        """
        Creates a list of potential clip begin and end sample indexes using a random number generator
        Args:
            :param recording:      an audio segment object that contains the audio samples to be processed
            :param max_clips:      create no more thanm this many clips from the recording
            :param pad_miliseconds: number of miliseconds to pad the begin and end of a clip
        """
        self.sci: List[SampleClippingInterval] = []

        total_frames = recording.frame_count()
        pad_frames = recording.frame_count(pad_miliseconds)

        for index in range(max_clips):
            beginning_frame = random.randint(0, total_frames - pad_frames)  # the start of source to milisecond pad before the end of source
            ending_frame = beginning_frame + random.randint(pad_frames, total_frames - beginning_frame)  # from milisecond pad up to the (source duration - the start of the clip)
            self.sci.append(SampleClippingInterval(beginning_frame, ending_frame))

    def get(self):
        return self.sci
