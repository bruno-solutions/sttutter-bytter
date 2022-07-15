from configuration import MAXIMUM_FRAMES


class SampleClippingInterval:
    """
    Value object for a sample clipping interval
    """

    def __init__(self, begin=0, end=MAXIMUM_FRAMES):
        """
        A sample index range within a source audio recording from which a clip can be produced
        Args:
        :param begin: the index of the first sample in the interval
        :param end:   the index of the last sample in the interval
        """
        self.begin = int(begin)
        self.end = int(end)

    def get(self):
        """
        :return: the sample interval in multiple formats
        """
        return self.begin, self.end, {'begin': self.begin, 'end': self.end}, [self.begin, self.end], (self.begin, self.end)
