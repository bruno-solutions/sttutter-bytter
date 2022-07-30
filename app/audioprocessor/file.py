import os
import shutil
from pathlib import Path

from logger import Logger


def md(path: str, name: str) -> bool:
    if path is None:
        return False
    if Path(path).is_dir():
        Logger.debug(f"{name} path {path} exists")
        return False
    if Path(path).exists():
        Logger.warning(f"{name} path {path} cannot be created")
        Logger.warning(f"A file of the same name exists and will not be overwritten")
        return True
    try:
        os.mkdir(path)
    except OSError as error:
        Logger.warning(f"{name} cannot be created")
        Logger.warning(f"Path {path} is either invalid or inaccessible (permissions)")
        Logger.warning(f"The system error was: {error}")
        return True
    return False


def rm_md(cache_root, export_root, log_root, temp_root) -> bool:
    def _rm_md(path, name, _erred=False):
        if path is None:
            return _erred
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            Logger.separator()
            Logger.warning(f"{name} directory does not exist and therefore cannot be removed")
            Logger.warning(f"Hopefully the path {path} is not invalid or inaccessible (permissions)")
            Logger.warning(f"I'll try to create {path} for you next")
            _erred = True
        except OSError as error:
            Logger.separator()
            Logger.warning(f"{name} directory cannot be removed")
            Logger.warning(f"Path {path} may be invalid, inaccessible (permissions), or in use")
            Logger.warning(f"The system error was: {error}")
            _erred = True
        return md(path, name) or _erred

    erred = _rm_md(log_root, 'Log root')
    erred = _rm_md(cache_root, 'Cache root') or erred
    erred = _rm_md(export_root, 'Export root') or erred
    erred = _rm_md(temp_root, 'Temp root') or erred

    return erred
