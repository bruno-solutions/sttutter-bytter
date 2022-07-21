"""
Download audio files from the internet
"""
import os
import shutil
import time
from urllib.parse import urlparse

import pydub
import youtube_dl

from configuration import DEFAULT_FRAME_RATE, AUDIO_FILE_TYPE, CACHE_ROOT, DOWNLOAD_BASE_FILE_NAME, METADATA_FILE_TYPE
from logger import Logger


def download(uri: str, directory=CACHE_ROOT, filename=DOWNLOAD_BASE_FILE_NAME, frame_rate=DEFAULT_FRAME_RATE, audio_file_type=AUDIO_FILE_TYPE, external_downloader=None, tagger=None, logger: Logger = Logger()):
    """
    Download source media from a URL (and when processing is active, extract and save the audio in a file for clipification)
    Args:
        :param uri:                 The desired song's source Uniform Resource Identifier
        :param directory:           The directory into which the source file will be downloaded
        :param filename:            The name of the downloaded source file (without a file extension)
        :param frame_rate:          Audio samples per second of the audio file extracted from the downloaded media file
        :param audio_file_type:     the type of audio file to produce from the downloaded media file
        :param external_downloader: The name of a library for YouTube Download to use to download the source file (instead of it's built-in downloader)
        :param tagger:              The tags for the audio file
        :param logger:              User supplied custom logger | Default audiobot Logger
    """
    if tagger is None:
        logger.error(f"A Tagger object was not provided to the download() function")
        raise ValueError("A Tagger object must be provided to the download() function for metadata management")

    metadata_filename = f"{filename}.{METADATA_FILE_TYPE}"

    parsed = urlparse(uri)
    if "file" == parsed.scheme:
        extension = os.path.splitext(parsed.path)[1]
        copied_file = f"{filename}.{extension}"
        converted_file = f"{filename}.{AUDIO_FILE_TYPE}"

        if os.path.isfile(copied_file):
            logger.debug(f"File {copied_file} is cached on the local file system", separator=True)
        else:
            source_file = parsed.netloc + parsed.path if parsed.netloc else parsed.path.strip('/')  # This might be Windows only logic

            logger.debug(f"Copying file on local file system", separator=True)
            logger.debug(f"From: {source_file}")
            logger.debug(f"To:   {copied_file}")

            try:
                shutil.copyfile(source_file, copied_file)
            except OSError or FileNotFoundError as error:
                logger.error(f"Could not copy {source_file} from local file system to cache directory {directory}")
                logger.error(f"The 'download' URI was {uri}")
                logger.error(f"The system error was: {error}")
                raise error

            logger.debug(f"Local file system copy completed")

        logger.debug(f"Converting file from {audio_file_type} to {AUDIO_FILE_TYPE}", separator=True)
        recording = pydub.AudioSegment.from_file(copied_file, format="wav").set_frame_rate(frame_rate).set_sample_width(2)
        recording.export(converted_file, format=AUDIO_FILE_TYPE).close()
        logger.debug(f"Converted file created {converted_file}")

        logger.debug(f"Generating metadata file (minicking YouTube Download option 'writeinfojson': True)", separator=True)

        tagger.read_audio_file_tags(copied_file)
        tagger.add('duration', int(recording.duration_seconds))
        tagger.add('filesize', os.path.getsize(copied_file))
        tagger.add('asr', recording.frame_rate)
        tagger.add('frame rate', recording.frame_rate)
        tagger.add('channels', recording.channels)
        tagger.add('sample width', recording.sample_width)
        tagger.add('rms', recording.rms)
        tagger.add('max', recording.max)
        tagger.add('max possible amplitude', recording.max_possible_amplitude)
        tagger.add('full scale decibels', recording.dBFS)
        tagger.add('max full scale decibels', recording.max_dBFS)
        tagger.add('converter', recording.converter)
        tagger.write_youtube_downloader_metadata(metadata_filename)
        return

    def progress_callback(attributes):
        if 'downloading' != attributes['status'] and 'finished' != attributes['status']:
            logger.debug(f"Download status: {attributes['status']}")

    # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

    parameters = {
        'cachedir': directory,
        'outtmpl': filename + '.%(ext)s',
        'sr': frame_rate,
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
        'external_downloader': external_downloader,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_file_type,  # see ffmpeg -f and -bsf options
                'preferredquality': '192',  # see ffmpeg -b -q options
            }
        ],
        'progress_hooks': [
            progress_callback
        ]
    }

    with youtube_dl.YoutubeDL(parameters) as downloader:
        try:
            start_time = time.time()
            logger.debug(f"Download started [{external_downloader if external_downloader is not None else 'default YouTube Download'}]", separator=True)
            downloader.download([uri])
            finish_time = time.time()
            logger.debug(f"Download and file conversion finished [{finish_time - start_time} s]")
        except youtube_dl.DownloadError as error:
            logger.error(message=str(error))
            raise error

    tagger.format_metadata_file(metadata_filename)
