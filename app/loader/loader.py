"""
Copy or download media (video or audio) files to the application cache directory
"""
import hashlib
import os
import shutil
import time
from urllib.parse import urlparse

from configuration.configuration import Configuration
from logger import Logger
from tagger import Tagger


class Loader(object):
    def __init__(self, tagger: Tagger = None):
        """
        Propvides the ability to load (download or copy) and convert source media (audio or video) files as audio files
        Args:
        :param tagger: the tags for the audio file
        """
        if tagger is None:
            Logger.error(f"A Tagger object was not provided when instantiating the Downloader class")
            raise ValueError("A Tagger object must be provided when instantiating the Downloader class, for metadata handling")

        self.tagger: Tagger = tagger

    import pydub

    def copy(self, uri: str, path_file_base: str, audio_file_name: str) -> pydub.AudioSegment:
        """
        Copy a media (video or audio) file from the local file system
        Args:
        :param uri:             the local file system path of the media file to be copied as a Uniform Resource Identifier
        :param path_file_base:  the base path and file for the media file to be loaded to which file extensions will be appended as required (media file vs metadata file)
        :param audio_file_name: the name of the copy/converted audio file
        """
        import pydub

        parsed_url = urlparse(uri)
        source_file_name = parsed_url.netloc + parsed_url.path if parsed_url.netloc else parsed_url.path.strip('/')  # This might be Windows only logic
        intermediate_file_name = f"{path_file_base}{os.path.splitext(parsed_url.path)[1]}"
        metadata_file_name = f"{path_file_base}.{Configuration().get('metadata_file_type')}"

        if os.path.isfile(intermediate_file_name):
            Logger.debug(f"File {intermediate_file_name} is cached on the local file system")
        else:
            Logger.debug(f"Copying file on local file system")
            Logger.debug(f"From: {source_file_name}")
            Logger.debug(f"To:   {intermediate_file_name}")

            try:
                shutil.copyfile(source_file_name, intermediate_file_name)
            except OSError or FileNotFoundError as error:
                Logger.error(f"Could not copy {source_file_name} from local file system to cache directory {Configuration().get('cache_root')}")
                Logger.error(f"The 'download' URI was {uri}")
                Logger.error(f"The system error was: {error}")
                raise error

        self.tagger.synchronize_metadata(intermediate_file_name, metadata_file_name)

        Logger.debug(f"Creating {Configuration().get('output_file_type')} audio file from copied file", separator=True)
        recording: pydub.AudioSegment = pydub.AudioSegment.from_file(intermediate_file_name).set_frame_rate(Configuration().get('frame_rate')).set_channels(Configuration().get('channels')).set_sample_width(Configuration().get('sample_width'))
        recording.export(audio_file_name, format=Configuration().get('output_file_type')).close()
        Logger.debug(f"Audio file created {audio_file_name}")

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
        downloader_module = Configuration().get('downloader_module')
        Logger.debug(f"Download started [{downloader_module if downloader_module is not None else 'default YouTube Download'}]", separator=True)

        def progress_monitor(attributes):
            if 'downloading' != attributes['status'] and 'finished' != attributes['status']:
                Logger.debug(f"Download status: {attributes['status']}")

        # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312

        parameters = {
            'cachedir': Configuration().get('cache_root'),
            'outtmpl': path_file_base + '.%(ext)s',
            'sr': Configuration().get('frame_rate'),
            'format': 'bestaudio/best',  # 249, 250, 251
            'writeinfojson': True,
            'writeannotations': True,
            # 'writesubtitles': True,
            # 'writeautomaticsub': True,
            # 'allsubtitles': True,
            'prefer_ffmpeg': True,
            'keepvideo': True,  # ffmpeg -k
            'verbose': True,
            'logger': Logger(),
            'external_downloader': downloader_module,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': Configuration().get('output_file_type'),  # see ffmpeg -f and -bsf options
                    'preferredquality': '192',  # see ffmpeg -b -q options
                }
            ],
            'progress_hooks': [
                progress_monitor
            ]
        }

        import youtube_dl

        with youtube_dl.YoutubeDL(parameters) as downloader:
            try:
                downloader.download([uri])
            except youtube_dl.DownloadError as error:
                Logger.error(message=str(error))
                raise error

        metadata_file_name: str = f"{path_file_base}.{Configuration().get('metadata_file_type')}"
        self.tagger.synchronize_metadata(audio_file, metadata_file_name)

        import pydub

        return pydub.AudioSegment.from_file(audio_file)

    def load(self, uri: str) -> tuple[pydub.AudioSegment, str]:
        """
        Download (or copy) a media (video or audio) file from a URL (or the local file system)
        Args:
        :param uri: the Uniform Resource Identifier of the media file to be loaded
        """
        Logger.debug(f"Loading media file from {uri}", separator=True)
        start_time: float = time.time()
        path_file_base: str = f"{Configuration().get('cache_root')}\\{hashlib.md5(uri.encode('utf-8')).hexdigest().upper()}"
        audio_file: str = f"{path_file_base}.{Configuration().get('output_file_type')}"

        import pydub

        try:
            recording: pydub.AudioSegment = self.copy(uri, path_file_base, audio_file) if uri.startswith("file://") else self.download(uri, path_file_base, audio_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Loading media file from URL: {uri} failed")

        Logger.debug(f"Audio file {audio_file} generated")
        Logger.debug(f"Media file load and conversion finished [{time.time() - start_time} secs]")

        return recording, audio_file
