import librosa
import numpy


class VolumeChangeDetector:
    """A handler that hosts the volume change slicer."""

    def __init__(self, data):
        self.data = data
        self.parse_data()
        self.filtered = None

    @staticmethod
    def angled_lp_filter(db_profile, weight=0.1):
        """Filter out unusually high and short volume spikes."""

        buoy = -20.

        for volume in db_profile:
            if buoy < volume <= buoy + weight:
                buoy = volume

            elif buoy + weight < volume:
                buoy += weight

        return buoy

    def parse_data(self, filter_width=441):
        """Extract data and convert it to desired formats"""

        # Convert and filter each section of the data
        self.filtered = [
            self.angled_lp_filter(db_profile)
            for db_profile in numpy.pad(librosa.amplitude_to_db(self.data), (0, len(self.data) % filter_width))
                .reshape((len(self.data) - 1) // filter_width + 1, filter_width)
        ]

    def write_critical_time(self, cti):
        """Writes volume change information to CTI."""
        """Trying to append the volume spikes onto cti but I'm not sure if it is appending one buoy or multiple 
        volume changes """
        for i in range(0, len(self.data)):
            cti.append(self.angled_lp_filter(self.data))
