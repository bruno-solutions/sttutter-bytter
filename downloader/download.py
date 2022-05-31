"""
    Download songs from the internet.

    Functions:
        getsong_with_aria2c(url, outfile_name, logger) --> None:
        getsong_with_ytdl(url, outfile_name, logger) --> None:
"""

from __future__ import unicode_literals
import youtube_dl
import logging


def getsong_with_aria2c(*args, **kwargs):
    """
    A faster version of getsong_with_ytdl() that utilizes external aria2c.
    Accept logging for youtube_dl to handle errors.
    """
    getsong_with_ytdl(*args, **kwargs, external_downloader='aria2c')


def getsong_with_ytdl(
        url,
        outfile_name='cache/ytdl-fullsong',
        logger=None,
        external_downloader=None
    ):
    """
    Use specified URL to download song from the internet and save as file.
    Accept logging for youtube_dl to handle errors.
    Debugging or warning functionalities pending further implementation.

    Args:
        url --> str:    The desired song's source URL   | *
        outfile_name:   File path for saving            | 'stWavFile'
        logger:         User supplied custom logger     | Default Built-in Logger
    """

    #Testing .webm file
    DEBUG_SKIP_YTDL_POST_PROCESSING = True

    #Use Monaural only for testing
    DEBUG_FORCE_MONO = True

    #Print all debug info on stdout
    DEBUG_VERBOSE = False

    class BuiltInLogger:
        """Custom logger class for future use."""

        @staticmethod
        def debug(msg):
            """Print debug message onto debug_log.txt for debugging."""
            if DEBUG_VERBOSE:
                logging.basicConfig(filename='debug_log.txt', filemode='w', format='%(asctime)s - %(name)s - %('
                                                                                   'levelname)s - %(message)s')
                logging.exception("[DEBUG]" + msg)

        @staticmethod
        def warning(msg):
            """
            Print warning message on stdout for debugging.
            """
            print("[WARN]: "+msg)

        @staticmethod
        def error(msg):
            """Print error message onto error_log.txt for debugging."""
            # print("[ERROR]: "+msg)
            logging.basicConfig(filename='error_log.txt', filemode='w', format='%(asctime)s - %(name)s - %('
                                                                               'levelname)s - %(message)s')
            logging.exception("[ERROR]" + msg)

    def my_hook(attrs):
        if attrs['status'] == 'finished':
            print(attrs)
            print("Done downloading, now converting ...")

    ydl_args = { # Properties for the output file
        'outtmpl': outfile_name + '.%(ext)s',
        'format': 'bestaudio/best',
        'external_downloader': external_downloader,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'logger': BuiltInLogger() if logger is None else logger,
        'progress_hooks': [my_hook],
    }

    if DEBUG_SKIP_YTDL_POST_PROCESSING:
        del ydl_args['postprocessors']

    if DEBUG_FORCE_MONO:
        ydl_args['postprocessor_args'] = {
            'ac', '1' # Mono audio
        }

    # Access youtube_dl and download the wav file
    with youtube_dl.YoutubeDL(ydl_args) as ydl:
        try:
            ydl.cache.remove()
            ydl.download([url])
        except youtube_dl.DownloadError as dl_error:
            logging.basicConfig(filename='error_log.txt', filemode='w', format='%(asctime)s - %(name)s - %('
                                                                               'levelname)s - %(message)s')
            logging.exception(str(dl_error))
