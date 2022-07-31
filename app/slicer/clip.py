from sci import SampleClippingInterval


class Clip(object):
    """
    Value object of a clip
    """
    import pydub

    def __init__(self, recording: pydub.AudioSegment, sci: SampleClippingInterval):
        """
        A sample index range within a source audio recording from which a clip can be produced
        Note: when reversed, begin and end will be swapped
        Note: interval will be limited to between 0 and MAXIMUM_SAMPLES
        Args:
        :param recording: the source recording from which the clip is being made
        :param sci:       the sample clipping (begin/end index pair) interval from the source recording
        """
        frame_rate = recording.frame_rate
        begin, end = sci.get()
        self.begin = {'index': begin, 'time': begin / frame_rate}
        self.end = {'index': end, 'time': end / frame_rate}
        self.segment = recording.get_sample_slice(start_sample=begin, end_sample=end)

    def get(self):
        """
        :return: the samples and the extract begin and end points (as a sample index and a time value) from the source recording
        """
        return {
            'samples': self.segment,
            'source': {
                'begin': self.begin,
                'end': self.end
            }
        }
