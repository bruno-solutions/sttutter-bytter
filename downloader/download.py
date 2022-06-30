"""
    Download audio files from the internet

    Functions:
        getsong_with_aria2c(url, outfile_name, logger) --> None:
        getsong_with_ytdl(url, outfile_name, logger) --> None:
"""

from __future__ import unicode_literals

import taglib
import youtube_dl

from app import CACHE_FILE_NAME, CACHE_WAV_FILE_NAME
from app import DEBUG_SKIP_YTDL_POST_PROCESSING
from downloader.logger import Logger


def getsong_with_aria2c(*args, **kwargs):
    """
    A faster version of getsong_with_ytdl() that utilizes external aria2c library
    """

    getsong_with_ytdl(*args, **kwargs, external_downloader='aria2c')


def getsong_with_ytdl(url, logger=None, external_downloader=None):
    """
    Use specified URL to download a song from the internet and save it as a file

    Args:
        :param url:          The desired song's source URL   | *
        :param logger:       User supplied custom logger     | Default Built-in Logger
        :param external_downloader:
    """

    def my_hook(attributes):
        if 'finished' == attributes['status']:
            print("[YouTube download]: Success")

    ydl_args = {
        'outtmpl': CACHE_FILE_NAME + '.%(ext)s',
        'format': 'bestaudio/best',
        'external_downloader': external_downloader,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata'
            }
        ],
        'logger': Logger() if logger is None else logger,
        'progress_hooks': [my_hook],
        'sr': 44100
    }

    if DEBUG_SKIP_YTDL_POST_PROCESSING:
        del ydl_args['postprocessors']

    with youtube_dl.YoutubeDL(ydl_args) as downloader:
        try:
            downloader.cache.remove()
            downloader.download([url])

            # Add source URL to the audio file metadata
            audio = taglib.File(CACHE_WAV_FILE_NAME)
            audio.tags["WPUB"] = [url]  # https://id3.org/id3v2.3.0#URL_link_frames
            audio.save()
        except youtube_dl.DownloadError as error:
            Logger.error(message=str(error))
