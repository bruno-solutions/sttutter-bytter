"""
    Download songs from the internet (note this is the fast download version).

    Functions:
        getsong_from_url(url, outfile_name, logger) --> None:
"""

from __future__ import unicode_literals
import youtube_dl


def getsong_from_url_fast(url, outfile_name='stWavFile', logger=None):
    """
    Use specified URL to download song from the internet and save as file.
    Accept logging for youtube_dl to handle errors.
    Debugging or warning functionalities pending further implementation.

    Args:
        url --> str:    The desired song's source URL   | *
        outfile_name:   File path for saving            | 'stWavFile'
        logger:         User supplied custom logger     | Default Built-in Logger

    External Downloader: You can add an external downloader at external_downloader
    in ydl_opts to have the overall application run faster (faster download speeds).
    The current available external downloaders are aria2c, avconv, axel, curl, ffmpeg,
    httpie, and wget. The default is set to aria2c but it will not mess up if you don't have any external
    downloaders or aria2c.

    """

    # Use Monaural only for testing
    DEBUG_FORCE_MONO = False

    class BuiltInLogger:
        """Custom logger class for future use."""

        """Pending implementation for debug and warning."""

        @staticmethod
        def debug(msg):
            print(msg)

        @staticmethod
        def warning(msg):
            print(msg)

        @staticmethod
        def error(msg):
            """Print error message on stdout for debugging."""
            print(msg)

    def my_hook(dic):
        if dic['status'] == 'finished':
            print(dic)
            print("Done downloading, now converting ...")

    ydl_args = {  # Properties for the output file
        'outtmpl': outfile_name + '.%(ext)s',
        'format': 'bestaudio/best',
        'external_downloader': 'aria2c',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'postproccessors_args': [{
            'ar': '44100'
        }],
        'logger': BuiltInLogger() if logger is None else logger,
        'progress_hooks': [my_hook],
    }

    if DEBUG_FORCE_MONO:
        ydl_args["postprocessor_args"] = {
            'ac', '1'  # Mono audio
        }

    # Access youtube_dl and download the wav file
    with youtube_dl.YoutubeDL(ydl_args) as ydl:
        try:
            ydl.cache.remove()
            ydl.download([url])
        except (youtube_dl.DownloadError, youtube_dl.utils.ExtractorError) as dl_error:
            print(dl_error)
