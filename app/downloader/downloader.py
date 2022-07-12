"""
    Download audio files from the internet

    Functions:
        get_song_with_aria2c(url, outfile_name, logger) --> None:
        get_song_with_ytdl(url, outfile_name, logger) --> None:
"""
import time

import youtube_dl

from configuration import DEFAULT_SAMPLE_RATE, EXPORT_FILE_TYPE, CACHE_FILE_NAME, CACHE_ROOT
from configuration import DISABLE_DOWNLOAD_POST_PROCESSING
from logger import Logger


def download(url, cache_root=CACHE_ROOT, cache_filename=CACHE_FILE_NAME, logger=Logger(), external_downloader=None):
    """
    Use specified URL to download a song from the internet and save it as a file
    Args:
        :param url:                 The desired song's source URL | *
        :param cache_root:          The directory into which the audio file will be downloaded
        :param cache_filename:      The name of the downloaded file (without a file extension)
        :param logger:              User supplied custom logger   | Default Built-in Logger
        :param external_downloader: A library for YouTube Download to use to download the recording (instead of it's built-in downloader)
    """

    def my_hook(attributes):
        if 'downloading' == attributes['status']:
            print(f".", end='', flush=True)
        elif 'finished' != attributes['status']:
            print(f"\nDownload status: {attributes['status']}")

    # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

    parameters = {
        'cachedir': cache_root,
        'outtmpl': cache_filename + '.%(ext)s',
        'format': 'bestaudio/best',
        'sr': DEFAULT_SAMPLE_RATE,
        'external_downloader': external_downloader,
        'writeinfojson': True,
        'prefer_ffmpeg': True,
        'logger': logger,
        'progress_hooks': [my_hook]
        #  'verbose': True
    }

    if not DISABLE_DOWNLOAD_POST_PROCESSING:
        parameters['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': EXPORT_FILE_TYPE,  # see ffmpeg -f and -bsf options
            'preferredquality': '192',  # see ffmpeg -b -q options
        }]

    with youtube_dl.YoutubeDL(parameters) as downloader:
        try:
            start_time = time.time()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S:', time.gmtime(start_time))} Download started [{external_downloader if external_downloader is not None else 'default YoutubeDL'}]")
            downloader.download([url])
            finish_time = time.time()
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S:', time.gmtime(finish_time))} Download {'and postprocessing ' if not DISABLE_DOWNLOAD_POST_PROCESSING else ''}finished [{finish_time - start_time} s]")
        except youtube_dl.DownloadError as error:
            Logger.error(message=str(error))
            raise error
