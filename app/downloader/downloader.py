"""
    Download audio files from the internet

    Functions:
        get_song_with_aria2c(url, outfile_name, logger) --> None:
        get_song_with_ytdl(url, outfile_name, logger) --> None:
"""
import json

import youtube_dl

from configuration import DEFAULT_SAMPLE_RATE, EXPORT_FILE_TYPE, CACHE_FILE_NAME, CACHE_WAV_FILE_NAME, YOUTUBE_DOWNLOAD_INFO_FILE_NAME, CACHE_ROOT
from configuration import DISABLE_YOUTUBE_DOWNLOAD_POST_PROCESSING
from logger import Logger
from tagger import Tagger


def get_song_aria2c(*args, **kwargs):
    """
    Utilize the aria2c library to download the audio recording faster
    """
    return get_song_with_ytdl(*args, **kwargs, external_downloader='aria2c')


def get_song_with_ytdl(url, logger=None, external_downloader=None):
    """
    Use specified URL to download a song from the internet and save it as a file
    Args:
        :param url:                 The desired song's source URL | *
        :param logger:              User supplied custom logger   | Default Built-in Logger
        :param external_downloader: A library for YouTube Download to use to download the recording (instead of it's built-in downloader)
    """

    def my_hook(attributes):
        if 'downloading' == attributes['status']:
            print(f".", end='', flush=True)
        else:
            print(f"\nDownload: {attributes['status']}")

    # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

    parameters = {
        'cachedir': CACHE_ROOT,
        'outtmpl': CACHE_FILE_NAME + '.%(ext)s',
        'format': 'bestaudio/best',
        'sr': DEFAULT_SAMPLE_RATE,
        'external_downloader': external_downloader,
        'writeinfojson': True,
        'prefer_ffmpeg': True,
        'logger': Logger() if logger is None else logger,
        'progress_hooks': [my_hook]
        #  'verbose': True
    }

    if not DISABLE_YOUTUBE_DOWNLOAD_POST_PROCESSING:
        parameters['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': EXPORT_FILE_TYPE,  # see ffmpeg -f and -bsf options
            'preferredquality': '192',           # see ffmpeg -b -q options
        }]

    with youtube_dl.YoutubeDL(parameters) as downloader:
        try:
            downloader.cache.remove()
            print("Download: started")
            downloader.download([url])
        except youtube_dl.DownloadError as error:
            Logger.error(message=str(error))
            raise error

        with open(YOUTUBE_DOWNLOAD_INFO_FILE_NAME) as json_file:
            tagger = Tagger(json.load(json_file))
            tagger.write_tags(CACHE_WAV_FILE_NAME)

    return tagger
