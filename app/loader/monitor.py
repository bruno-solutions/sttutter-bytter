import re

from logger import Logger, timestamp


def cleanse(message: str) -> str:
    return re.sub(r'\s*\[[^][]*]\s*', '', message)


class Monitor(object):
    downloading: bool = False
    blanking_size: int = 0

    @staticmethod
    def progress(attributes: {}) -> None:
        status: str = attributes["status"]

        downloading: bool = "downloading" == status
        finished: bool = "finished" == status

        blanking_string: str = f"{' ' * Monitor.blanking_size}\r" if (downloading or finished) and Monitor.blanking_size else ""
        message: str = f"{timestamp()} [INFO]: "

        if downloading:
            message += f"{attributes['_percent_str']} of {attributes['_total_bytes_str']} at {attributes['_speed_str']}"
            if "00:00" != attributes['_eta_str']:
                message += f" ETA {attributes['_eta_str']}"
        elif finished:
            if Monitor.downloading:
                message += f"Downloaded {attributes['_total_bytes_str']} in {attributes['_elapsed_str']}"
            else:
                message += f"Loaded {attributes['_total_bytes_str']} from disk cache"
        else:
            message += f"Status: [{status}]"

        print(f"{blanking_string}{message}", end='\r' if downloading else '\n', flush=True)

        Monitor.blanking_size = len(message) if downloading else 0
        Monitor.downloading = downloading

    @staticmethod
    def debug(message: str) -> None:
        if "[download]" not in message:
            Logger.info(cleanse(message))

    @staticmethod
    def warning(message: str) -> None:
        Logger.warning(cleanse(message))

    @staticmethod
    def error(message: str) -> None:
        Logger.error(cleanse(message))
