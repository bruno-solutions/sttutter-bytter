import logging
import time
from pathlib import Path
from typing import Union

from configuration.configuration import Configuration


def timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))


class Logger(object):
    """
    Message logging class
    """

    @staticmethod
    def separator(separator: Union[str, bool] = Configuration().get('log_file_separator'), length: int = 80, mode: str = ''):
        """
        Emit a log separator
        """
        if not separator or ('debug' == mode and not Configuration().get('log_debug')) or ('warning' == mode and not Configuration().get('log_warning')) or ('error' == mode and not Configuration().get('log_error')):
            return

        separator = ''.join([(separator if separator is str and separator != '' else Configuration().get('log_file_separator')) * length])

        if Configuration().get('log_to_console'):
            print(separator)

        log_file_path = Configuration().get('log_file_path')

        if log_file_path and Path(log_file_path).parent.is_dir():
            logging.basicConfig(filemode='w', filename=log_file_path, level=logging.DEBUG if Configuration().get('log_debug') else logging.WARNING if Configuration().get('log_warning') else logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.info(separator)

    @staticmethod
    def debug(message: str, separator: Union[str, bool] = False):
        """
        Log a debug message
        """
        if not Configuration().get('log_debug'):
            return

        Logger.separator(separator)

        message: str = message.lstrip()

        if Configuration().get('log_to_console'):
            if message.startswith('[download]'):
                print(f"\r{timestamp()} [DEBUG]: {message}", end='' if "100%" not in message else '\n', flush=True)
            else:
                print(f"{timestamp()} [DEBUG]: {message}")

        log_file_path = Configuration().get('log_file_path')

        if log_file_path and Path(log_file_path).parent.is_dir():
            logging.basicConfig(filemode='w', filename=log_file_path, level=logging.DEBUG if Configuration().get('log_debug') else logging.WARNING if Configuration().get('log_warning') else logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.debug(message)

    @staticmethod
    def warning(message: str, separator: Union[str, bool] = False):
        """
        Log a warning
        """
        if not Configuration().get('log_warning'):
            return

        Logger.separator(separator)

        message: str = message.lstrip()

        if Configuration().get('log_to_console'):
            print(f"{timestamp()} [WARNING]: {message}")

        log_file_path = Configuration().get('log_file_path')

        if log_file_path and Path(log_file_path).parent.is_dir():
            logging.basicConfig(filemode='w', filename=log_file_path, level=logging.DEBUG if Configuration().get('log_debug') else logging.WARNING if Configuration().get('log_warning') else logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.warning(message)

    @staticmethod
    def error(message: str, separator: Union[str, bool] = False):
        """
        Log an error
        """
        if not Configuration().get('log_error'):
            return

        Logger.separator(separator)

        message: str = message.lstrip()

        if Configuration().get('log_to_console'):
            print(f"{timestamp()} [ERROR]: {message}")

        log_file_path = Configuration().get('log_file_path')

        if log_file_path and Path(log_file_path).parent.is_dir():
            logging.basicConfig(filemode='w', filename=log_file_path, level=logging.DEBUG if Configuration().get('log_debug') else logging.WARNING if Configuration().get('log_warning') else logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.error(message)

    import pydub

    @staticmethod
    def properties(recording: pydub.AudioSegment, message: str = None):
        Logger.separator()

        if message is not None:
            Logger.debug(message)

        number_of_samples: int = len(recording.get_array_of_samples())
        number_of_samples_per_channel: int = number_of_samples // recording.channels
        duration: float = number_of_samples_per_channel / recording.frame_rate

        Logger.debug(f"Frame rate: {recording.frame_rate}")
        Logger.debug(f"Channels: {recording.channels} ({'monaural' if 1 == recording.channels else 'stereo'})")
        Logger.debug(f"Sample count: {number_of_samples}, per channel: {number_of_samples_per_channel}")
        Logger.debug(f"Duration: {(duration // 60):0.0f}:{(duration % 60):0.0f} or precisely {duration:f} seconds")
