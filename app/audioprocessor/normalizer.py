"""
The module that provides audio volume leveling functionality:
    - class Normalizer
"""

import pydub


class Normalizer:
    """
    The class that implements ReplayGain
    """
    pydub = getattr(pydub.AudioSegment, 'normalize')

    def __init__(self, normalizer=pydub):
        self.normalizer = normalizer

    def normalize(self, segment, normalizer=None):
        """
        The volume normalizer
        Args:
            segment --> pydub.AudioSegment | *
        """
        return normalizer(segment) if normalizer is not None else self.normalizer(segment)
