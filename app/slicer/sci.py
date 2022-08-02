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
