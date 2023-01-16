from typing import List

from .arguments import parse_common_arguments, to_hertz
from logger import Logger
from .sci import SampleClippingInterval


class PitchSlicer(object):
    """
    Pitch change slicer
    Locates fundamental frequency (key or pitch) change events to define sample clipping intervals
    """
    import pydub

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment) -> None:
        """
        Creates a list of potential clip begin and end sample indexes using tempo (beats per minute) change detection
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        """
        import librosa
        from numpy import ndarray

        self.sci: List[SampleClippingInterval] = []

        weight, segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording)

        min_frequency: int = to_hertz(arguments['min_frequency']) if 'min_frequency' in arguments else 65  # hz (C2)
        max_frequency: int = to_hertz(arguments['max_frequency']) if 'max_frequency' in arguments else 2093  # hz (C7)
        frame_length: int = arguments['frame_length'] if 'frame_length' in arguments else recording.frame_rate // 11

        total_samples: int = int(segment.frame_count())

        Logger.info(f"Slicing stage[{stage}], Pitch Change Slicer: {clips} clips", separator=True)

        Logger.debug(f"Segment Samples: {total_samples}")

        # https://librosa.org/doc/main/generated/librosa.to_mono.html
        # https://librosa.org/doc/main/generated/librosa.yin.html

        # noinspection PyUnusedLocal
        changes: ndarray = librosa.yin(y=librosa.to_mono(y=recording.get_array_of_samples()), fmin=min_frequency, fmax=max_frequency, sr=recording.frame_rate, frame_length=frame_length)

        clips = 0  # TODO turn the pitch change points array into sample clipping intervals
        for clip_index in range(clips):
            # difference = math.fabs(changes[2] - changes[1])
            # pos = -1
            # for index in range(1, changes.size - 1):
            #     if (math.fabs(changes[index + 1] - changes[index])) > difference:
            #         difference = math.fabs(changes[index + 1] - changes[index])
            #         pos = index + 1
            # return 4 / 173 if -1 == pos else pos * (4 / 173)

            sci = SampleClippingInterval(begin=0, end=0)
            self.sci.append(sci)
            Logger.debug(f"Interval[{clip_index}]: {sci.begin} {sci.end}")

    def get(self):
        return self.sci
