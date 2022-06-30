import logging

from app import DEBUG_VERBOSE

LOGGING_MESSAGE_TEMPLATE = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class Logger:
    """
    Custom logger class
    """

    @staticmethod
    def debug(message):
        """
        Write debug message to debug.log
        """
        if DEBUG_VERBOSE:
            logging.basicConfig(filename='debug.log', filemode='w', format=LOGGING_MESSAGE_TEMPLATE)
            logging.exception("[DEBUG]" + message)

    @staticmethod
    def warning(message):
        """
        Print warning message to stdout
        """
        print("[WARN]: " + message)

    @staticmethod
    def error(message):
        """
        Write error message to error.log
        """

        logging.basicConfig(filename='error.log', filemode='w', format=LOGGING_MESSAGE_TEMPLATE)
        logging.exception("[ERROR]: " + message)
