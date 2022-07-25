from pathlib import Path


def normalize_file_path(file_path: str, extension: str) -> str:
    """
    Expand the full path and ensure the file extension is set correctly
    Args:
    :param file_path: the name of the file to be normalized
    :param extension: the extension to add to the normalized file path
    """
    path = Path(file_path).resolve()  # expand relative paths to full paths
    extension = extension if extension.startswith('.') else f".{extension}"  # guarantee '.' on the extension
    parent = path.parent.resolve()  # expand relative paths to full paths
    full_file_path = str(parent.joinpath(f"{path.name}{extension}" if extension != path.suffix else path.name))
    return str(full_file_path)
