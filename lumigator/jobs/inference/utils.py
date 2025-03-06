import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

from litellm.exceptions import APIError
from loguru import logger


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


T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3, base_delay: float = 1.0, backoff_factor: float = 2.0, exceptions_to_catch: tuple = (APIError,)
) -> Callable:
    """Retry decorator with exponential backoff.

    Args:
        max_retries: Maximum number of retries before giving up
        base_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions_to_catch: Tuple of exceptions that trigger a retry
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            retry_count = 0
            delay = base_delay

            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions_to_catch as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Maximum retries ({max_retries}) exceeded")
                        raise

                    logger.warning(f"API error (attempt {retry_count}/{max_retries}): {e}")
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    return decorator
