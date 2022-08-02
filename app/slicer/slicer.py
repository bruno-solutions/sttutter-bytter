"""
Slicer module
"""
from __future__ import annotations

from typing import List, Optional, Union, Literal

from beat import BeatSlicer
from chaos import ChaosSlicer
from clip import Clip
from configuration import Configuration
from interval import SimpleIntervalSlicer
from logger import Logger
from onset import OnsetSlicer
from pitch import PitchSlicer
from sci import SampleClippingInterval
from tempo import TempoSlicer
from .vocal import VocalSlicer
from .volume import VolumeSlicer


class Slicer(object):
    """
    Builds a list of weighted sample clipping intervals based upon the results of the invoked slicing methods
    from which lists of auido array sample arrays (known as clips) are prepared from a source audio recording
    """

    def __init__(self):
        """
        Instantiate the Slicer class
        Args:
        """
        import pydub

        self.recording: Optional[pydub.AudioSegment] = None
        self.sci: List[SampleClippingInterval] = []

    import pydub

    def slice(self, recording: pydub.AudioSegment = None, logic: [{}] = None, sci: List[SampleClippingInterval] = None) -> Slicer:
        """
        Apply slicer methods to build a set of recording sample clipping intervals
        Args:
        :param recording: the audio recording to be sliced
        :param logic:     the slicers to use to slice the recording and the slicer arguments
        :param sci:       starter sample clipping intervals
        """
        if recording is None:
            raise RuntimeError("Recording not provided, use the Loader class to load a file to slice")
        if Configuration().get('minimum_recording_size_miliseconds') > len(recording):  # refuse to slice recordings shorter than 1 second (for no particular reason)
            raise RuntimeError("Recording was less than 1000 miliseconds, will not slice")
        if logic is None or 0 == len(logic):
            raise RuntimeError("Slicer methods not declared, create a method dictionary that describes how to process and slice the recording")

        self.recording = recording
        self.sci = [] if sci is None else sci

        Logger.info("Slicing sample clipping intervals from the recording")

        for stage, slicer in enumerate(logic):  # execution each slicer is a "stage" in the processing of the source
            if "active" in slicer and not slicer["active"]:  # skip methods that are deactivated
                continue
            if "weight" in slicer and 0 == int(slicer["weight"]):  # skip methods that have no weight
                continue

            try:
                method_name = slicer["method"]
            except AttributeError:
                Logger.warning(f"Attribute 'method' not defined on slicer[{stage}]")
                Logger.warning(f"Available methods are: 'slice_on_beat', 'slice_at_random', 'slice_on_vocal_change', 'slice_on_volume_change'")
                continue

            try:
                method = getattr(Slicer, method_name)
            except AttributeError:
                Logger.warning(f"No slicer method named '{method_name}' is avaialable in the slicer module, referenced in slicer[{stage}]")
                Logger.warning(f"Available methods are: 'slice_on_beat', 'slice_at_random', 'slice_on_vocal_change', 'slice_on_volume_change'")
                continue

            try:
                arguments = slicer["arguments"]
            except KeyError:
                Logger.debug(f"'arguments' not provided for '{method_name}', using default values")
                arguments = {}

            arguments["weight"] = slicer["weight"] if "weight" in slicer else "1"

            Logger.properties(recording, f"Pre-stage:{stage} [{method_name}] slicing recording characteristics")
            method(self, stage, arguments)
            Logger.properties(recording, f"Post-stage:{stage} [{method_name}] slicing recording characteristics")

        Logger.debug(f"Sliced {len(self.sci)} sample clipping intervals from the recording")
        return self

    def cluster_indexes(self, sample_indexes: [int], proximity: Union[int, None] = None) -> [[int]]:
        """
        Group Sample Clipping Intervals by beginning or ending sample index to "vote" for likely clip edges
        Args:
        :param sample_indexes: a list of begin or end Sample Clipping Intervals to cluster
        :param proximity:   the nearness in miliseconds by which to cluster Sample Clipping Intervals
        """
        sample_indexes.sort()
        sample_index_proximity_threshold = (self.recording.frame_rate // 1000) * (proximity if proximity is not None else Configuration().get("cluster_window_miliseconds"))

        cluster: [int] = []
        trailing_sample_indexes_index: int = len(sample_indexes) - 1
        while 0 <= trailing_sample_indexes_index:
            trailing_sample_index: int = sample_indexes[trailing_sample_indexes_index]
            leading_sample_indexes_index: int = trailing_sample_indexes_index
            while 0 <= leading_sample_indexes_index:
                current_sample_index: int = sample_indexes[leading_sample_indexes_index]
                if sample_index_proximity_threshold < trailing_sample_index - current_sample_index:
                    yield cluster
                    cluster = []
                    break
                cluster += [current_sample_index]
                leading_sample_indexes_index -= 1
            if cluster:
                yield cluster
                cluster = []

            # Scan for the next (potentially) overlapping cluster at a fraction of the proximity threshold away from the last trailing sample indexes index

            trailing_sample_index -= sample_index_proximity_threshold // 4
            while 0 <= trailing_sample_indexes_index and trailing_sample_index < sample_indexes[trailing_sample_indexes_index]:
                trailing_sample_indexes_index -= 1

        if cluster:
            yield cluster

    @staticmethod
    def cluster_size_histogram(sci_index_clusters) -> ({int: int}, int, int, float):
        histogram: {} = {}
        for sci_cluster in sci_index_clusters:
            key: int = len(sci_cluster)
            histogram[key] = histogram[key] + 1 if key in histogram else 1

        low: int = len(sci_index_clusters)
        high: int = 0
        accumulator: int = 0
        for key in sorted(histogram, reverse=True):
            frequency: int = histogram[key]
            if low > frequency:
                low = frequency
            if high < frequency:
                high = frequency
            accumulator += frequency
            del histogram[key]
            histogram[key] = frequency

        return histogram, low, high, accumulator // len(histogram)

    @staticmethod
    def cluster_prune(index_clusters: [[int]], threshold: int) -> [[int]]:
        clusters: [[int]] = []
        minimums: [int] = []
        maximums: [int] = []

        for index_cluster in index_clusters:
            if threshold <= len(index_cluster):
                clusters += [index_cluster]
                minimums += [min(index_cluster)]
                maximums += [max(index_cluster)]
        return clusters, minimums, maximums

    def clip_boundries(self, side: Literal["begin", "end"]) -> ([int], [int]):
        indexes: [int] = []
        indexes += (getattr(sci, side) for sci in self.sci)
        index_clusters: List[List[int]] = []
        index_clusters += self.cluster_indexes(indexes)
        index_cluster_sizes_histogram, low, high, average = Slicer.cluster_size_histogram(index_clusters)
        pruned_index_clusters, lowest_cluster_index, highest_cluster_index = Slicer.cluster_prune(index_clusters, average)

        return pruned_index_clusters, lowest_cluster_index if "begin" == side else highest_cluster_index

    def get(self, start: int = None, length: int = None) -> [Clip]:
        """
        Generate audio segment clips from the recording based upon the Sample Clipping Intervals determined by slice()
        Args:
        :param start:  the zero based index of the first clip to return (to support pagination/memory management)
        :param length: the maximum number of clips to return (to support pagination/memory management)
        """
        start = 0 if start is None else start
        length = len(self.sci) if length is None else length

        Logger.properties(self.recording, "Clip creation recording characteristics")

        # Find clusters in the begin and end lists from the Sample Clipping Intervals

        pruned_index_clusters_begin, lowest_index_in_cluster_begin = self.clip_boundries("begin")
        pruned_index_clusters_end, highest_index_in_cluster_end = self.clip_boundries("end")

        maximum_clip_size_samples: int = (self.recording.frame_rate // 1000) * Configuration().get("maximum_clip_size_miliseconds")
        clips_considered: int = 0
        clips_generated: int = 0
        intervals: List[SampleClippingInterval] = []
        for begin_sample_index in lowest_index_in_cluster_begin:
            for end_sample_index in highest_index_in_cluster_end:
                if end_sample_index > begin_sample_index and maximum_clip_size_samples >= end_sample_index - begin_sample_index:
                    if start <= clips_considered:
                        intervals += [SampleClippingInterval(begin=begin_sample_index, end=end_sample_index)]
                        clips_generated += 1
                    if length <= clips_generated:
                        break
                    clips_considered += 1
            if length <= clips_generated:
                break

        clips: [Clip] = []
        for interval in intervals:
            clips += [Clip(self.recording, interval)]
        return clips

    slice_on_beat_weight: int = 5

    def slice_on_beat(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on the musical every beat slicer:
        Identifies single beats and groups these into consecutive ranges in overlapping multiples of the requested beat count
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += BeatSlicer(stage, arguments, self.recording).get()

    slice_at_interval_weight: int = 1

    def slice_at_interval(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice equally spaced clips slicer:
        Processes based upon the clip size slicer, the desired number of clips, and the duration of the downloaded audio recording
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += SimpleIntervalSlicer(stage, arguments, self.recording).get()

    slice_at_random_weight: int = 1

    def slice_at_random(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice randomly slicer:
        Adds noise to the clip weightings for statistical balancing
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += ChaosSlicer(stage, arguments, self.recording).get()

    slice_on_vocal_change_weight: int = 1

    def slice_on_vocal_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on vocal cues slicer:
        Processes by filtering vocal and then performing volume change detection
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += VocalSlicer(stage, arguments, self.recording).get()

    slice_on_volume_change_weight: int = 5

    def slice_on_volume_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on volume change slicer:
        Processes by measuring volume fluctuations in 'detection_window' sized chunks of the recording
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += VolumeSlicer(stage, arguments, self.recording).get()

    slice_at_onset_weight: int = 4

    def slice_at_onset(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on onset detection slicer:
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += OnsetSlicer(stage, arguments, self.recording).get()

    slice_on_tempo_change_weight: int = 3

    def slice_on_tempo_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on tempo change detection slicer:
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += TempoSlicer(stage, arguments, self.recording).get()

    slice_on_pitch_change_weight: int = 2

    def slice_on_pitch_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on pitch change detection slicer:
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += PitchSlicer(stage, arguments, self.recording).get()

    @staticmethod
    def get_slicer_methods() -> list[(str, int)]:
        """
        Returns a list of the available slicer methods to assist users in writing slicing scripts:
        Note: all slicer wrapper method names must begin with "slice_"
        """
        return [(attribute, getattr(Slicer, f"{getattr(Slicer, attribute).__name__}_weight")) for attribute in dir(Slicer) if attribute.startswith("slice_") and callable(getattr(Slicer, attribute))]
