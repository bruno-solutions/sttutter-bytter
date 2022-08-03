from typing import List, Union, Literal

from configuration import Configuration


class SampleClippingInterval(object):
    """
    Value object for a sample clipping interval
    """

    def __init__(self, begin=None, end=None):
        """
        A sample index range within a source audio recording from which a clip can be produced
        Note: when reversed, begin and end will be swapped
        Note: interval will be limited to between 0 and MAXIMUM_SAMPLES
        Args:
        :param begin: the index of the first sample in the interval
        :param end:   the index of the last sample in the interval
        """
        maximum_samples = Configuration().get('maximum_samples')

        if begin is None:
            begin = 0
        if end is None:
            end = maximum_samples
        if begin > end:
            begin, end = end, begin
        if 0 > begin:
            begin = 0
        if end > maximum_samples:
            end = maximum_samples

        self.begin = int(begin)
        self.end = int(end)

    def get(self):
        """
        :return: the sample interval
        """
        return self.begin, self.end


def cluster_indexes(indexes: [int], frame_rate: int, proximity: Union[int, None] = None) -> [[int]]:
    """
    Group Sample Clipping Intervals by beginning or ending sample index to "vote" for likely clip edges
    Args:
    :param indexes:    a list of begin or end Sample Clipping Intervals to cluster
    :param proximity:  the nearness in miliseconds by which to cluster Sample Clipping Intervals
    :param frame_rate: the frame rate of the source recording
    """
    indexes.sort()
    proximity_threshold = (frame_rate // 1000) * (proximity if proximity is not None else Configuration().get("cluster_window_miliseconds"))

    cluster: [int] = []
    trailing_indexes_index: int = len(indexes) - 1
    while 0 <= trailing_indexes_index:
        trailing_index: int = indexes[trailing_indexes_index]
        leading_indexes_index: int = trailing_indexes_index
        while 0 <= leading_indexes_index:
            current_index: int = indexes[leading_indexes_index]
            if proximity_threshold < trailing_index - current_index:
                yield cluster
                cluster = []
                break
            cluster += [current_index]
            leading_indexes_index -= 1
        if cluster:
            yield cluster
            cluster = []

        # Scan for the next (potentially) overlapping cluster at a fraction of the proximity threshold away from the last trailing sample indexes index

        trailing_index -= proximity_threshold // 4
        while 0 <= trailing_indexes_index and trailing_index < indexes[trailing_indexes_index]:
            trailing_indexes_index -= 1

    if cluster:
        yield cluster


def cluster_size_histogram(clusters: List[List[int]]) -> ({int: int}, int, int, float):
    histogram: {} = {}
    for cluster in clusters:
        key: int = len(cluster)
        histogram[key] = histogram[key] + 1 if key in histogram else 1

    low: int = len(clusters)
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

    frequencies: int = len(histogram)
    return histogram, low, high, accumulator // frequencies if frequencies else 0


def filter_clusters(clusters: [[int]], threshold: int) -> [[int]]:
    filtered_clusters: [[int]] = []

    for cluster in clusters:
        if threshold <= len(cluster):
            filtered_clusters += [cluster]

    return filtered_clusters, [min(filtered_clusters)], [max(filtered_clusters)]


def clip_boundries(sci: List[SampleClippingInterval], frame_rate: int, side: Literal["begin", "end"]) -> ([int], [int]):
    indexes: [int] = [getattr(interval, side) for interval in sci]
    index_clusters: List[List[int]] = []
    index_clusters += cluster_indexes(indexes, frame_rate)
    index_cluster_sizes_histogram, low, high, average = cluster_size_histogram(index_clusters)
    pruned_index_clusters, lowest_cluster_index, highest_cluster_index = filter_clusters(index_clusters, average)

    return pruned_index_clusters, lowest_cluster_index if "begin" == side else highest_cluster_index


def clip_intervals_from_onsets(sci: List[SampleClippingInterval], frame_rate: int, start: int, length: int) -> List[SampleClippingInterval]:
    pruned_index_clusters_begin, lowest_index_in_cluster_begin = clip_boundries(sci, frame_rate, "begin")
    pruned_index_clusters_end, highest_index_in_cluster_end = clip_boundries(sci, frame_rate, "end")

    maximum_clip_size_samples: int = (frame_rate // 1000) * Configuration().get("maximum_clip_size_miliseconds")
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

    return intervals
