import os
import shutil

from configuration import EXPORT_ROOT, CACHE_ROOT


def purge_files(cache_root=CACHE_ROOT, export_root=EXPORT_ROOT):
    cache_root = f"{os.getcwd()}\\{cache_root}"
    export_root = f"{os.getcwd()}\\{export_root}"

    try:
        shutil.rmtree(cache_root)
    except FileNotFoundError:
        print(f"[NOTICE]: {cache_root} directory does not exist (but that's OK, I'll make it for you)")
        pass

    try:
        shutil.rmtree(export_root)
    except FileNotFoundError:
        print(f"[NOTICE]: {export_root} directory does not exist (but that's OK, I'll make it for you)")
        pass
