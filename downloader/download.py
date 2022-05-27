"""
    Download songs from the internet.

    Functions:
        getsong_from_url(url, outfile_name, logger) --> None:
"""

from __future__ import unicode_literals
import youtube_dl


def getsong_from_url(url, outfile_name='stWavFile', logger=None):
    """
    Use specified URL to download song from the internet and save as file.
    Accept logging for youtube_dl to handle errors.
    Debugging or warning functionalities pending further implementation.

    Args:
        url --> str:    The desired song's source URL   | *
        outfile_name:   File path for saving            | 'stWavFile'
        logger:         User supplied custom logger     | Default Built-in Logger
    """
    if not youtube_dl:
        raise ModuleNotFoundError("Youtube-dl not found in you environment. "
                                  "You need to install youtube-dl to your environment")
    else:
        # Testing .webm file
        DEBUG_SKIP_YTDL_POST_PROCESSING = True

        # Use Monaural only for testing
        DEBUG_FORCE_MONO = True

        class BuiltInLogger:
            """Custom logger class for future use."""

            """Pending implementation."""

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

        def my_hook(attrs):
            if attrs['status'] == 'finished':
                print(attrs)
                print("Done downloading, now converting ...")

        ydl_args = {  # Properties for the output file
            'outtmpl': outfile_name + '.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessors_args': [{
                'ar': '44100'
            }],
            'logger': BuiltInLogger() if logger is None else logger,
            'progress_hooks': [my_hook],
        }

        if DEBUG_SKIP_YTDL_POST_PROCESSING:
            del ydl_args['postprocessors']

        if DEBUG_FORCE_MONO:
            ydl_args['postprocessor_args'] = {
                'ac', '1'  # Mono audio
            }

        # Access youtube_dl and download the wav file
        with youtube_dl.YoutubeDL(ydl_args) as ydl:
            try:
                ydl.cache.remove()
                ydl.download([url])
            except (youtube_dl.DownloadError, youtube_dl.utils.ExtractorError) as dl_error:
                print(dl_error)
