import os
import shutil

from configuration.configuration import Configuration
from logger import Logger


def rm_md(cache_root=Configuration().get('cache_root'), export_root=Configuration().get('export_root'), log_root=Configuration().get('log_root'), temp_root=Configuration().get('temp_root'), logger: Logger = None):
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
