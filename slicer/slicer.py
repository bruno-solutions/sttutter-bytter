"""Slicer homonymous submodule."""

import random, numpy
import pydub, librosa


class Slicer:
    """The primary object of the slicer module."""

    def __init__(self, base_seg, count):
        ### Get all
        self.base_seg = base_seg
        self.count = count

        self.data = None
        self.convert_data()

        self.intervals = []
        self.clips = []

    @classmethod
    def invoke_slicers(cls, slicer_methods):
        """
        A method invoker that wraps and registers a
        custom slicer method in pydub's effects list.
        """

        if isinstance(slicer_methods, dict):
            for named_method in slicer_methods.items():
                cls.invoke_slicers(named_method)

        elif isinstance(slicer_methods, tuple):
            name, method = slicer_methods

            @pydub.utils.register_pydub_effect(name)
            def slicer_method_wrap(seg, count, *args, **kwargs):
                return getattr(cls(seg, count), method)(*args, **kwargs). \
                    execute_slicing().clips

        else:
            raise TypeError

    def convert_data(self):
        """Converts the data info librosa-compatible format."""

        data_raw_stereo = numpy.array(
            self.base_seg.get_array_of_samples()
        )

        data_raw_left  = data_raw_stereo[::2]
        data_raw_right = data_raw_stereo[1::2]

        data_raw_mono = (
            data_raw_left + data_raw_right
        ) / 2

        # Convert int32 data to float (-1. ~ 1.)
        self.data = data_raw_mono /\
            numpy.iinfo(numpy.int32).max

    def execute_slicing(self):
        """Execute slicing."""

        ### Use clip intervals to segment the clip
        for i in self.intervals:
            self.clips.append(
                self.base_seg[i[0]:i[1]]
            )

        return self

    def random_slice(self):
        """
        Create slices at random.
        This slicer method is meant to be a template
        for the creation of other slicer methods.
        """

        # Access data, equivalent to data=librosa.load()
        # Alternatively, self.data can be used in place
        # of 'data' directly.
        data = self.data

        # The total amount of clips desired is stored
        # in self.count. Loop for self.count.
        for index in range(self.count):
            # Calculate random range.
            duration_ms = int(
                self.base_seg.duration_seconds * 1000
            )

            start_ms = random.randint(
                0, duration_ms - 1000
            )

            end_ms = start_ms + random.randint(
                1000, 10000  # 1 to 10 seconds long.
            )

            # Append clip ranges to self.intervals.
            self.intervals.append((start_ms, end_ms))

        # Mandatory return-self.
        return self


class CriticalTimes:
    """Saves, mixes, and convert critical time indexes into intervals."""

    def __init__(self, host):
        self.host = host

    def generate_from_beats(self):
        """
        Return a list of pair list of critical times in ms.
        E.g. [[star1, end1],[star2, end2], [star3, end3]...]
        """

        beat = librosa.beat.beat_track(y=self.host.data, sr=44100)[1] * 1000

        critical_time = []

        ### Get every fourth beat and return it in critical_time
        for i in range(4, len(beat), 8):
            critical_time.append([beat[i - 4], beat[i] + 500])
        return critical_time
