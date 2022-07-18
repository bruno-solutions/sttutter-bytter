"""
    Download audio files from the internet

    Functions:
        get_song_with_aria2c(url, outfile_name, logger) --> None:
        get_song_with_ytdl(url, outfile_name, logger) --> None:
"""
import os
import shutil
import time
from urllib.parse import urlparse

import youtube_dl

from configuration import DEFAULT_FRAME_RATE, AUDIO_FILE_TYPE, CACHE_ROOT, DOWNLOAD_BASE_FILE_NAME, METADATA_FILE_TYPE
from logger import Logger


def download(uri: str, postprocess=True, sample_rate=DEFAULT_FRAME_RATE, directory=CACHE_ROOT, filename=DOWNLOAD_BASE_FILE_NAME, audio_file_type=AUDIO_FILE_TYPE, external_downloader=None, tagger=None, logger=Logger()):
    """
    Download source media from a URL (and when processing is active, extract and save the audio in a file for clipification)
    Args:
        :param uri:                 The desired song's source Uniform Resource Identifier
        :param postprocess:         Extract the audio from the downloaded file
        :param sample_rate:         audio samples per second of the audio file extracted from the downloaded media file
        :param audio_file_type:     the type of audio file to produce from the downloaded media file
        :param directory:           The directory into which the source file will be downloaded
        :param filename:            The name of the downloaded source file (without a file extension)
        :param external_downloader: The name of a library for YouTube Download to use to download the source file (instead of it's built-in downloader)
        :param tagger:              The tags for the audio file
        :param logger:              User supplied custom logger | Default audiobot Logger
    """
    logger.separator(mode='debug')

    if tagger is None:
        logger.error(f"A Tagger object was not provided to the download() function")
        raise ValueError("A Tagger object must be provided to the download() function for metadata management")

    parsed = urlparse(uri)
    if "file" == parsed.scheme:
        extension = os.path.splitext(parsed.path)[1]
        destination = f"{filename}{extension}"

        if os.path.isfile(destination):
            logger.debug(f"File {destination} is cached on the local file system")
        else:
            source = parsed.netloc + parsed.path if parsed.netloc else parsed.path.strip('/')

            logger.separator(mode='debug')
            logger.debug(f"Copying file on local file system")
            logger.debug(f"From: {source}")
            logger.debug(f"To:   {destination}")

            try:
                shutil.copyfile(source, destination)
            except OSError or FileNotFoundError as error:
                logger.error(f"Could not copy {source} from local file system to cache directory {directory}")
                logger.error(f"The 'download' URI was {uri}")
                logger.error(f"The system error was: {error}")
                raise error

            logger.debug(f"Local file system copy completed")

        logger.debug(f"Generating YouTube Download metadata file (Minicking 'writeinfojson': True)")

        tagger.read_audio_file_tags(destination).write_youtube_downloader_metadata(f"{filename}{METADATA_FILE_TYPE}")

        return

    def progress_callback(attributes):
        if 'downloading' != attributes['status'] and 'finished' != attributes['status']:
            logger.debug(f"Download status: {attributes['status']}")

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
            downloader.download([uri])
            finish_time = time.time()
            logger.debug(f"Download {'and postprocessing ' if postprocess else ''}finished [{finish_time - start_time} s]")
        except youtube_dl.DownloadError as error:
            logger.error(message=str(error))
            raise error
