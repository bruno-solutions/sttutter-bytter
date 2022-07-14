from typing import List

import librosa
import pydub

from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval


class BeatSlicer:
    """
    Beat interval slicer
    """

    def __init__(self, recording: pydub.AudioSegment, frequency=4, attack=50):
        """
        Creates a list potential clip begin and end sample indexes using "musical" beat boundaries
        Args:
            :param recording: an audio segment object that contains the audio samples to be processed
            :param frequency: the number of beats per clipping interval
            :param attack:    the number of miliseconds after the onset of the end beat to include in the clipping interval to ensure that the end beat is fully included in the clipping interval
        """
        self.sci: List[SampleClippingInterval] = []

        frame_rate = recording.frame_rate
        padding_frames = recording.frame_count(attack)
        monaural_samples = Normalizer.monaural_normalization(recording.get_array_of_samples(), recording.sample_width)
        frames = librosa.beat.beat_track(y=monaural_samples, sr=frame_rate)
        samples = librosa.frames_to_samples(frames)

        for index in range(frequency, len(samples), frequency):
            self.sci.append(SampleClippingInterval(samples[index - frequency], samples[index] + padding_frames))

    def get(self):
        return self.sci
