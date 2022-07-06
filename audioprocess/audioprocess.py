"""
The main audio processing module
"""

import pydub
import taglib
from pydub.utils import mediainfo

from configuration import CACHE_WAV_FILE_NAME, WAV_FILE_NAME, URL

from .replaygain import ReplayGain


class AudioProcessor:
    """
    The class that handles overall audio processing
    """

    def __init__(self, filename, sample_rate):
        self.clips = list()
        self.audio_segment = None

        self.load_audio_segment(filename, sample_rate)

    def load_audio_segment(self, filename, sample_rate):
        """
        Loads a wave file as AudioSegmant object
        """

        self.audio_segment = pydub.AudioSegment.from_file(file=filename).set_frame_rate(sample_rate)
        return self

    def preprocess(self, handler=ReplayGain):
        """
        Execute audio normalization
        """

        self.audio_segment = handler().normalize(self.audio_segment)
        return self

    def apply_slicer(self, sample_rate, duration, threshold, slicer=None, count=10):
        """
        Loads and executes the slicer module
        """

        if not slicer:
            raise RuntimeError("Default slicer loader not implemented.")

        self.clips = slicer(sample_rate, duration, threshold, self.audio_segment, count)
        return self

    def postprocess(self, fadein_duration=500, fadeout_duration=500, export_path="cache"):
        """
        Append fade-in and fade-out
        """

        for index, clip in enumerate(self.clips):
            self.clips[index] = clip.fade_in(fadein_duration).fade_out(fadeout_duration)

        self.export()
        return self

    def export(self):
        """
        Export the sliced audio clips into the desired directory
        """

        # Create dict. of metadata using mediainfo api and add URL into comments
        # if 'comment' in info_dict:
        #     info_dict.pop('comment')
        # info_dict['comment'] = URL
        # info_dict["ID3"] = {'WOAS': URL}

        o_audio = taglib.File(CACHE_WAV_FILE_NAME)
        info_dict = o_audio.tags
        # print(info_dict)

        for index, clip in enumerate(self.clips):
            clip.export(out_f=f"cache/export/{index}.wav", format='wav')

            audio = taglib.File(f"cache/export/{index}.wav")
            audio.tags["URL"] = [URL]
            audio.tags["ARTIST"] = [str(info_dict['ARTIST']).strip("[]")]
            audio.tags["COMMENT"] = [str(info_dict['COMMENT']).strip("[]")]
            audio.tags["DATE"] = [str(info_dict['DATE']).strip("[]")]
            audio.tags["TITLE"] = [str(info_dict['TITLE']).strip("[]")]
            audio.save()

        return self
