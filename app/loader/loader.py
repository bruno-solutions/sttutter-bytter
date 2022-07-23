"""
Copy or download media (video or audio) files to the application cache directory
"""
import hashlib
import os
import shutil
import time
from typing import Tuple
from urllib.parse import urlparse

import pydub
import youtube_dl

from configuration import DEFAULT_FRAME_RATE, OUTPUT_FILE_TYPE, CACHE_ROOT, METADATA_FILE_TYPE, DEFAULT_CHANNELS, DEFAULT_SAMPLE_WIDTH
from logger import Logger
from tagger import Tagger


class Loader:
    def __init__(self, cache_root: str = CACHE_ROOT, audio_file_type: str = OUTPUT_FILE_TYPE, channels: int = DEFAULT_CHANNELS, frame_rate: int = DEFAULT_FRAME_RATE, sample_width: int = DEFAULT_SAMPLE_WIDTH, downloader_module: str = None, tagger: Tagger = None, logger: Logger = None):
        """
        Propvides the ability to load (download or copy) and convert source media (audio or video) files as audio files
        Args:
        :param cache_root:        the directory into which the source file will be downloaded
        :param audio_file_type:   the type of audio file to produce from the downloaded media file
        :param frame_rate:        audio samples per second of the audio file extracted from the downloaded media file
        :param sample_width:      the number of bytes per sample (1 for 8-bit, 2 for 16-bit (CD quality), and 4 for 32-bit)
        :param downloader_module: the name of a library for YouTube Download to use to download the source file (instead of it's built-in downloader)
        :param tagger:            the tags for the audio file
        :param logger:            user supplied custom logger | default application Logger
        """
        logger: Logger = logger if logger is not None else Logger()

        if tagger is None:
            logger.error(f"A Tagger object was not provided when instantiating the Downloader class")
            raise ValueError("A Tagger object must be provided when instantiating the Downloader class, for metadata handling")

        self.cache_root: str = cache_root
        self.audio_file_type: str = audio_file_type
        self.channels: int = channels
        self.frame_rate: int = frame_rate
        self.sample_width: int = sample_width
        self.downloader_module: str = downloader_module
        self.tagger: Tagger = tagger
        self.logger: Logger = logger

    def copy(self, uri: str, path_file_base: str, audio_file_name: str):
        """
        Copy a media (video or audio) file from the local file system
        Args:
        :param uri:            the local file system path of the media file to be copied as a Uniform Resource Identifier
        :param path_file_base: the base path and file for the media file to be loaded to which file extensions will be appended as required (media file vs metadata file)
        :param audio_file_name:     the name of the copy/converted audio file
        """
        parsed_url = urlparse(uri)
        source_file_name = parsed_url.netloc + parsed_url.path if parsed_url.netloc else parsed_url.path.strip('/')  # This might be Windows only logic
        intermediate_file_name = f"{path_file_base}.{os.path.splitext(parsed_url.path)[1]}"
        metadata_file_name = f"{path_file_base}.{METADATA_FILE_TYPE}"

        if os.path.isfile(intermediate_file_name):
            self.logger.debug(f"File {intermediate_file_name} is cached on the local file system")
        else:
            self.logger.debug(f"Copying file on local file system")
            self.logger.debug(f"From: {source_file_name}")
            self.logger.debug(f"To:   {intermediate_file_name}")

            try:
                shutil.copyfile(source_file_name, intermediate_file_name)
            except OSError or FileNotFoundError as error:
                self.logger.error(f"Could not copy {source_file_name} from local file system to cache directory {self.cache_root}")
                self.logger.error(f"The 'download' URI was {uri}")
                self.logger.error(f"The system error was: {error}")
                raise error

        self.tagger.synchronize_metadata(intermediate_file_name, metadata_file_name)

        self.logger.debug(f"Creating {self.audio_file_type} audio file from copied file", separator=True)
        recording: pydub.AudioSegment = pydub.AudioSegment.from_file(intermediate_file_name).set_frame_rate(self.frame_rate).set_channels(self.channels).set_sample_width(self.sample_width)
        recording.export(audio_file_name, format=self.audio_file_type).close()
        self.logger.debug(f"Audio file created {audio_file_name}")

        self.tagger.synchronize_metadata(audio_file_name, metadata_file_name)

        return recording

    def download(self, uri: str, path_file_base: str, audio_file: str):
        """
        Download a media (video or audio) file from a URL
        Args:
        :param uri:            the network Uniform Resource Identifier of the media file to be downloaded
        :param path_file_base: the base path and file for the media file to be loaded to which file extensions will be appended as required (media file vs metadata file)
        :param audio_file:     the name of the downloaded audio file
        """
        self.logger.debug(f"Download started [{self.downloader_module if self.downloader_module is not None else 'default YouTube Download'}]", separator=True)

        def progress_monitor(attributes):
            if 'downloading' != attributes['status'] and 'finished' != attributes['status']:
                self.logger.debug(f"Download status: {attributes['status']}")

        # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

        parameters = {
            'cachedir': self.cache_root,
            'outtmpl': path_file_base + '.%(ext)s',
            'sr': self.frame_rate,
            'format': 'bestaudio/best',  # 249, 250, 251
            'writeinfojson': True,
            'writeannotations': True,
            # 'writesubtitles': True,
            # 'writeautomaticsub': True,
            # 'allsubtitles': True,
            'prefer_ffmpeg': True,
            'keepvideo': True,  # ffmpeg -k
            'verbose': True,
            'logger': self.logger,
            'external_downloader': self.downloader_module,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.audio_file_type,  # see ffmpeg -f and -bsf options
                    'preferredquality': '192',  # see ffmpeg -b -q options
                }
            ],
            'progress_hooks': [
                progress_monitor
            ]
        }

        with youtube_dl.YoutubeDL(parameters) as downloader:
            try:
                downloader.download([uri])
            except youtube_dl.DownloadError as error:
                self.logger.error(message=str(error))
                raise error

        metadata_file_name: str = f"{path_file_base}.{METADATA_FILE_TYPE}"
        self.tagger.synchronize_metadata(audio_file, metadata_file_name)

        return pydub.AudioSegment.from_file(audio_file)

    def load(self, uri: str) -> Tuple[pydub.AudioSegment, str]:
        """
        Download (or copy) a media (video or audio) file from a URL (or the local file system)
        Args:
        :param uri: the Uniform Resource Identifier of the media file to be loaded
        """
        self.logger.debug(f"Loading media file from {uri}", separator=True)
        start_time: float = time.time()
        path_file_base: str = f"{self.cache_root}\\{hashlib.md5(uri.encode('utf-8')).hexdigest().upper()}"
        audio_file: str = f"{path_file_base}.{OUTPUT_FILE_TYPE}"
        recording: pydub.AudioSegment = self.copy(uri, path_file_base, audio_file) if uri.startswith("file://") else self.download(uri, path_file_base, audio_file)

        self.logger.debug(f"Audio file {audio_file} generated")
        self.logger.debug(f"Media file load and conversion finished [{time.time() - start_time} secs]")

        return recording, audio_file
