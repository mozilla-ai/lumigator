import functools
import time

from loguru import logger
from paths import PathPrefix, strip_path_prefix


def resolve_model_repo(path: str) -> str:
    """Resolve an `AssetPath` to a loadable string path without the prefix.

    Args:
        path (str): The path to resolve.

    Returns:
        str: The resolved path.
    """
    if not path.startswith(PathPrefix.HUGGINGFACE):
        allowed_prefixes = {x.value for x in PathPrefix}
        raise ValueError(f"Unable to resolve asset path from {path}. Allowed prefixes: {allowed_prefixes}")

    return strip_path_prefix(path)


def timer(func):
    """Decorator which times the execution of the wrapped func.
    Execution time is logged and also returned together with func's returned value
    (output will be a tuple).
    """

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        logger.info(f"Elapsed time for {func.__name__}: {elapsed_time:0.4f} seconds")
        return value, elapsed_time

    return wrapper_timer
