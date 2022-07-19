from configuration import MAXIMUM_SAMPLES


class SampleClippingInterval:
    """
    Value object for a sample clipping interval
    """

    def __init__(self, begin=0, end=MAXIMUM_SAMPLES):
        """
        A sample index range within a source audio recording from which a clip can be produced
        Note: when reversed, begin and end will be swapped
        Note: interval will be limited to between 0 and MAXIMUM_SAMPLES
        Args:
        :param begin: the index of the first sample in the interval
        :param end:   the index of the last sample in the interval
        """
        if begin > end:
            begin, end = end, begin
        if 0 > begin:
            begin = 0
        if end > MAXIMUM_SAMPLES:
            end = MAXIMUM_SAMPLES

        self.begin = int(begin)
        self.end = int(end)

    def get(self):
        """
        :return: the sample interval in multiple formats
        """
        return self.begin, self.end, {'begin': self.begin, 'end': self.end}, [self.begin, self.end], (self.begin, self.end)
