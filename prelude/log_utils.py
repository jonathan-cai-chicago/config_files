import logging
import traceback
from typing import Optional


def create_console_logger(
    name: str = "prelude",
    level: int = logging.INFO,
    show_line_number: bool = True,
    datefmt: str = "%Y-%m-%d %H:%M:%S",
) -> logging.Logger:
    """
    Convenience function to create and configure a logger that prints to console.

    Args:
        name (str): Name of the logger. For example, `__name__` of the calling module.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        format (str): Log message format.
        datefmt (str): Date format for the log messages.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()

    if show_line_number:
        format = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s"
    else:
        format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    formatter = logging.Formatter(format, datefmt)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)

    return logger


def report_traceback(
    e: Exception,
    logger: Optional[logging.Logger] = None,
    prefix_message: str = "Task failed with exception:",
) -> None:
    """
    Log detailed information about an exception, including its type, message, and full traceback.

    This function logs comprehensive details of an exception, including the exception type,
    message, and traceback. It is useful for error reporting in production environments,
    especially where stack traces might otherwise be suppressed.

    Parameters
    ----------
    e : Exception
        The exception to report. This must be an instance of a class derived from the base
        `Exception` class.
    logger : Optional[logging.Logger], optional
        The logger object to use for logging the exception details. If `None`, a default logger
        is created using the current module name. Defaults to `None`.
    prefix_message : str, optional
        A message prefix for the error log. Defaults to "Task failed with exception:".

    Returns
    -------
    None

    Example
    -------
    >>> try:
    >>>     1 / 0
    >>> except ZeroDivisionError as e:
    >>>     report_traceback(e)

    Notes
    -----
    - This function logs messages at the ERROR level. Ensure that the logger's level is set
      appropriately to capture these messages.
    - If `logger` is `None`, a default logger is configured with the module's `__name__`.

    Raises
    ------
    TypeError
        If the first argument is not an instance of `Exception`.
    """
    if not isinstance(e, Exception):
        raise TypeError("The first argument must be an instance of Exception")

    if logger is None:
        logger = logging.getLogger(__name__)

    error_type = type(e).__name__
    error_message = str(e)
    traceback_info = traceback.format_exc()

    logger.error(prefix_message)
    logger.error(f"Error Type: {error_type}")
    logger.error(f"Error Message: {error_message}")
    logger.error("Traceback:")
    logger.error(traceback_info)
