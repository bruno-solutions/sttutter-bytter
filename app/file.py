import os
import shutil

from configuration import EXPORT_ROOT, CACHE_ROOT, LOG_ROOT
from logger import Logger


def cleanup(cache_root=CACHE_ROOT, export_root=EXPORT_ROOT, log_root=LOG_ROOT):
    logger = Logger()

    def recreate_root(root, name):
        if root is not None:
            try:
                shutil.rmtree(root)
            except FileNotFoundError:
                logger.debug(f"[NOTICE]: {root} directory does not exist (that's OK, I'll create it for you)")
                pass

            try:
                os.mkdir(root)
            except OSError as error:
                logger.error(f"[FATAL]: {name} cannot be created. I suspect that {root} is malformed or inaccessible")
                raise error

    recreate_root(cache_root, 'Cache root')
    recreate_root(export_root, 'Export root')
    recreate_root(log_root, 'Log root')
