from typing import List

import librosa
import pydub

from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval


class BeatSlicer:
    """
    Beat interval slicer
    """

    def __init__(self, recording: pydub.AudioSegment, stage: int, beat_count: int, attack_miliseconds: int, clips: int):
        """
        Creates a list of potential clip begin and end sample indexes using "musical" beat boundaries
        Args:
        :param recording:          an audio segment object that contains the audio samples to be processed
        :param beat_count:         the number of beats per clipping interval
        :param attack_miliseconds: the number of miliseconds after the onset of the end beat to include in the clipping interval to ensure that the end beat is fully included in the clipping interval
        :param clips:          create no more than this many clips from the recording
        """
        self.sci: List[SampleClippingInterval] = []

        frame_rate = recording.frame_rate
        padding_frames = recording.frame_count(attack_miliseconds)
        monaural_samples = Normalizer.monaural_normalization(recording)
        frames = librosa.beat.beat_track(y=monaural_samples, sr=frame_rate)[1]
        samples = librosa.frames_to_samples(frames)

        for index in range(beat_count, len(samples), beat_count):
            self.sci.append(SampleClippingInterval(samples[index - beat_count], samples[index] + padding_frames))
            if len(self.sci) >= clips:
                return

    def get(self):
        return self.sci
