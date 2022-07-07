"""
    Download audio files from the internet

    Functions:
        getsong_with_aria2c(url, outfile_name, logger) --> None:
        getsong_with_ytdl(url, outfile_name, logger) --> None:
"""

from __future__ import unicode_literals

import json

import youtube_dl

from configuration import DEBUG_SKIP_YTDL_POST_PROCESSING, CACHE_FILE_NAME, YOUTUBE_DL_INFO_FILE_NAME, CACHE_WAV_FILE_NAME, EXPORT_FILE_TYPE
from downloader.logger import Logger
from tags import write_tags, parse_metadata


def getsong(*args, **kwargs):
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
        'writeinfojson': True,
        'external_downloader': external_downloader,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': EXPORT_FILE_TYPE,
                'preferredquality': '192',
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

            with open(YOUTUBE_DL_INFO_FILE_NAME) as json_file:
                tags = parse_metadata(json.load(json_file))  # Get YoutubeDL content metadata from json file

            write_tags(CACHE_WAV_FILE_NAME, tags)
        except youtube_dl.DownloadError as error:
            Logger.error(message=str(error))

    return tags
