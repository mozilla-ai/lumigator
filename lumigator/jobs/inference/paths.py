import re


def strip_path_prefix(path: str) -> str:
    """Strip the 'scheme://' prefix from the start of a string."""
    pattern = r"^\w+\:\/\/"
    return re.sub(pattern, "", path)
