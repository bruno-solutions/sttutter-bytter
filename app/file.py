import os
import shutil
from pathlib import Path

from configuration import EXPORT_ROOT, CACHE_ROOT, LOG_ROOT, TEMP_ROOT
from logger import Logger


def normalize_file_path(file_path: str, extension: str) -> str:
    """
    Expand the full path and ensure the file extension is set correctly
    Args:
    :param file_path: the name of the file to be normalized
    :param extension: the extension to add to the normalized file path
    """
    extension = extension if extension.startswith('.') else f".{extension}"  # guarantee '.' on the extension
    path = Path(file_path).resolve()  # expand relative paths to full paths
    return str(path.parent.joinpath(path.name, f"{extension if extension != path.suffix else ''}"))


def rm_md(cache_root=CACHE_ROOT, export_root=EXPORT_ROOT, log_root=LOG_ROOT, temp_root=TEMP_ROOT, logger: Logger = None):
    logger: Logger = logger if logger is not None else Logger()  # create a logger when one is not provided

    def _rm_md(path, name):
        _erred = False

        if path is not None:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                if not _erred:
                    logger.separator()
                logger.warning(f"{name} directory does not exist and therefore cannot be removed")
                logger.warning(f"Path {path} may be invalid or inaccessible")
                logger.warning(f"That's OK, I'll try to create {path} for you")
                _erred = True
            except OSError as error:
                if not _erred:
                    logger.separator()
                logger.warning(f"{name} directory cannot be removed")
                logger.warning(f"Path {path} may be invalid, inaccessible, or in use")
                logger.warning(f"The system error was: {error}")
                _erred = True

            try:
                os.mkdir(path)
            except OSError as error:
                if not _erred:
                    logger.separator()
                logger.warning(f"{name} cannot be created")
                logger.warning(f"Path {path} may already exist or be invalid or inaccessible")
                logger.warning(f"The system error was: {error}")
                _erred = True

        return _erred

    erred = _rm_md(cache_root, 'Cache root')
    erred = _rm_md(export_root, 'Export root') or erred
    erred = _rm_md(log_root, 'Log root') or erred
    erred = _rm_md(temp_root, 'Temp root') or erred

    return erred
