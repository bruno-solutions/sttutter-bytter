import os
import shutil

from configuration import DEFAULT_EXPORT_ROOT, DEFAULT_CACHE_ROOT


def refresh_roots(cache_root=DEFAULT_CACHE_ROOT, export_root=DEFAULT_EXPORT_ROOT):
    def refresh_root(root, name):
        try:
            shutil.rmtree(root)
            os.mkdir(root)
        except FileNotFoundError:
            print(f"[NOTICE]: {root} directory does not exist (but that's OK, I'll make it for you)")
            pass
        except OSError as error:
            print(f"[FATAL]: {name} {root} is malformed or inaccessible")
            raise error

    refresh_root(cache_root, 'cache root')
    refresh_root(export_root, 'export root')
