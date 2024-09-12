import functools
import time

from loguru import logger


def timer(func):
    """
    Decorator which times the execution of the wrapped func.
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
