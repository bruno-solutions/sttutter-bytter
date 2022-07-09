import logging

from configuration import LOG_FILE, LOG_TO_CONSOLE, LOG_DEBUG, LOG_WARNING, LOG_ERROR


class Logger:
    """
    Custom logger class
    """

    @staticmethod
    def debug(message):
        """
        Log a debug message (when Debug is active)
        """
        if LOG_DEBUG:
            Logger.log(f"[DEBUG] : {message}")

    @staticmethod
    def warning(message):
        """
        Log a warning
        """
        if LOG_WARNING:
            Logger.log(f"[WARNING]: {message}")

    @staticmethod
    def error(message):
        """
        Log an error
        """
        if LOG_ERROR:
            Logger.log(f"[ERROR]: {message}")

    @staticmethod
    def log(message):
        """
        Log a message
        """
        if LOG_TO_CONSOLE:
            print(message)

        if LOG_FILE is not None:
            logging.basicConfig(filename=LOG_FILE, filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.exception(message)
