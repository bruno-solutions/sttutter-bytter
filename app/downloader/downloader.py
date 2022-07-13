"""
    Download audio files from the internet

    Functions:
        get_song_with_aria2c(url, outfile_name, logger) --> None:
        get_song_with_ytdl(url, outfile_name, logger) --> None:
"""
import time

import youtube_dl

from configuration import DEFAULT_SAMPLE_RATE, AUDIO_FILE_TYPE, CACHE_ROOT, DEFAULT_FILE_NAME
from logger import Logger


def download(url, postprocess=True, sample_rate=DEFAULT_SAMPLE_RATE, directory=CACHE_ROOT, filename=DEFAULT_FILE_NAME, audio_file_type=AUDIO_FILE_TYPE, logger=Logger(), external_downloader=None):
    """
    Download source media from a URL (and when processing is active, extract and save the audio in a file for clipification)
    Args:
        :param url:                 The desired song's source URL | *
        :param postprocess:         Extract the audio from the downloaded file
        :param sample_rate:         audio samples per second of the audio file extracted from the downloaded media file
        :param audio_file_type:     the type of audio file to produce from the downloaded media file
        :param directory:           The directory into which the source file will be downloaded
        :param filename:            The name of the downloaded source file (without a file extension)
        :param logger:              User supplied custom logger | Default audiobot Logger
        :param external_downloader: The name of a library for YouTube Download to use to download the source file (instead of it's built-in downloader)
    """

    def progress_callback(attributes):
        if 'downloading' != attributes['status'] and 'finished' != attributes['status']:
            logger.debug(f"\nDownload status: {attributes['status']}")

    # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

    parameters = {
        'cachedir': directory,
        'outtmpl': filename + '.%(ext)s',
        'sr': sample_rate,
        'format': 'bestaudio/best',
        'writeinfojson': True,
        'writeannotations': True,
        # 'writesubtitles': True,
        # 'writeautomaticsub': True,
        # 'allsubtitles': True,
        'prefer_ffmpeg': True,
        'keepvideo': True,  # ffmpeg -k
        'verbose': True,
        'logger': logger,
        'progress_hooks': [progress_callback],
        'external_downloader': external_downloader
    }

    if postprocess:
        parameters['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_file_type,  # see ffmpeg -f and -bsf options
            'preferredquality': '192',  # see ffmpeg -b -q options
        }]

    with youtube_dl.YoutubeDL(parameters) as downloader:
        try:
            start_time = time.time()
            logger.debug(f"Download started [{external_downloader if external_downloader is not None else 'default YoutubeDL'}]")
            downloader.download([url])
            finish_time = time.time()
            logger.debug(f"Download {'and postprocessing ' if postprocess else ''}finished [{finish_time - start_time} s]")
        except youtube_dl.DownloadError as error:
            logger.error(message=str(error))
            raise error
