import logging
import time

from configuration import LOG_TO_CONSOLE, LOG_FILE_NAME, LOG_DEBUG, LOG_WARNING, LOG_ERROR


class Logger:
    """
    Custom logger class
    """

    def __init__(self, log_to_console=LOG_TO_CONSOLE, log_file_name=LOG_FILE_NAME, log_debug=LOG_DEBUG, log_warning=LOG_WARNING, log_error=LOG_ERROR):
        self.log_to_console = log_to_console
        self.log_file_name = log_file_name
        self.log_debug = log_debug
        self.log_warning = log_warning
        self.log_error = log_error

    def debug(self, message):
        """
        Log a debug message
        """
        if not self.log_debug:
            return

        message = message.lstrip()

        if self.log_to_console:
            if message.startswith('[download]'):
                print(f"\r{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))} [DEBUG] {message}", end='' if "100%" not in message else '\n', flush=True)
            else:
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))} [DEBUG] {message}")

        if self.log_file_name is not None:
            logging.basicConfig(filename=self.log_file_name, filemode='w', level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.debug(message)

    def warning(self, message):
        """
        Log a warning
        """
        if not self.log_warning:
            return

        if self.log_to_console:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))} [WARNING] {message}")

        if self.log_file_name is not None:
            logging.basicConfig(filename=self.log_file_name, filemode='w', level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.warning(message)

    def error(self, message):
        """
        Log an error
        """
        if not self.log_error:
            return

        if self.log_to_console:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))} [ERROR] {message}")

        if self.log_file_name is not None:
            logging.basicConfig(filename=self.log_file_name, filemode='w', level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
            logging.error(message)

    def characteristics(self, recording, message=None):
        if message is not None:
            self.debug(message)

        number_of_samples = len(recording.get_array_of_samples())
        number_of_samples_per_channel = number_of_samples / recording.channels
        duration = number_of_samples_per_channel / recording.frame_rate
        self.debug(f"Frame rate: {recording.frame_rate}")
        self.debug(f"Channels: {recording.channels} ({'monaural' if 1 == recording.channels else 'stereo'})")
        self.debug(f"Sample count: {number_of_samples}, per channel: {number_of_samples_per_channel:5.5f}")
        self.debug(f"Duration: {(duration // 60):0.0f}:{(duration % 60):0.0f} or precisely {duration:f} seconds")
