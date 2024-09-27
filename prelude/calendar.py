import os
import gc
import csv
import polars as pl
from typing import List, Tuple, Generator, Any, Dict
from datetime import date, timedelta
from importlib import resources

from prelude import cfg
from prelude.log_utils import create_console_logger


logger = create_console_logger(name=__name__)


def get_calendar_path(exchange: str) -> str:
    """
    Get the path to the calendar file for the given exchange.

    Parameters
    ----------
    exchange : str
        The name of the exchange.

    Returns
    -------
    str
        The path to the calendar file.

    Notes
    -----
    The calendar file should be put in the `src/prelude/assets` directory.
    """
    with resources.path("prelude.assets", f"{exchange}_calendar.parquet") as path:
        return str(path)


def get_date_list(
    start_date: int,
    end_date: int,
    exchange: str,
    exclude_bad_dates: bool = True,
    include_half_days: bool = True,
) -> List[int]:
    """
    Get a list of trading dates between the given start and end dates.

    Parameters
    ----------
    start_date : int
        The start date in YYYYMMDD format.
    end_date : int
        The end date in YYYYMMDD format.
    exchange : str
        The name of the exchange.
    exclude_bad_dates : bool, optional
        Whether to exclude invalid trading dates, by default True.
    include_half_days : bool, optional
        Whether to include half trading days, by default True.

    Returns
    -------
    List[int]
        A list of trading dates in YYYYMMDD format.

    Notes
    -----
    The input Parquet file is expected to have the following columns:
    - TradeDate: int, YYYYMMDD format
    - isValid: int, 1 if the date is valid, 0 otherwise
    - isHalfDay: int, 1 if the date is a half day, 0 otherwise
    """
    start_date = int(start_date)
    end_date = int(end_date)
    df_cal = pl.read_parquet(get_calendar_path(exchange)).filter(pl.col("TradeDate").is_between(start_date, end_date))

    if exclude_bad_dates:
        df_cal = df_cal.filter(pl.col("isValid") == 1)

    if not include_half_days:
        df_cal = df_cal.filter(pl.col("isHalfDay") == 0)

    return df_cal["TradeDate"].to_list()


def get_date_by_offset(
    run_date: int,
    offset: int,
    exchange: str,
    exclude_bad_dates: bool = False,
    include_half_days: bool = True,
) -> int:
    """
    Get a trading date by applying an offset to a given date.

    Parameters
    ----------
    run_date : int
        The reference date in YYYYMMDD format.
    offset : int
        The number of trading days to offset from the reference date.
        Positive for future dates, negative for past dates.
    exchange : str
        The name of the exchange.
    exclude_bad_dates : bool, optional
        Whether to exclude invalid trading dates, by default False.
    include_half_days : bool, optional
        Whether to include half trading days, by default True.

    Returns
    -------
    int
        The resulting date in YYYYMMDD format after applying the offset.

    """
    df_cal = pl.read_parquet(get_calendar_path(exchange))

    if exclude_bad_dates:
        df_cal = df_cal.filter(pl.col("isValid") == 1)

    if not include_half_days:
        df_cal = df_cal.filter(pl.col("isHalfDay") == 0)

    idx0 = df_cal.select((pl.col("TradeDate") == run_date).arg_true()).item()
    return df_cal["TradeDate"][idx0 + offset]


def create_train_val_date_splits(
    dates: List[Any], train_window: int, val_window: int, fold_incomplete: bool = False
) -> Generator[Tuple[List[Any], List[Any]], None, None]:
    """
    Generate training and validation date splits from a list of dates, including all data.

    Args:
        dates (List[Any]): A list of dates in chronological order.
        train_window (int): The number of items for the training window.
        val_window (int): The number of items for the validation window.
        fold_incomplete (bool): If True, folds incomplete final validation data into the previous split.

    Yields:
        Tuple[List[Any], List[Any]]: A tuple containing the training dates and validation dates for each split.

    Examples:
        >>> list(create_train_val_date_splits(list(range(10)), 3, 2, fold_incomplete=False))
        [([0, 1, 2], [3, 4]), ([2, 3, 4], [5, 6]), ([4, 5, 6], [7, 8]), ([6, 7, 8], [9])]
        >>> list(create_train_val_date_splits(list(range(10)), 3, 2, fold_incomplete=True))
        [([0, 1, 2], [3, 4]), ([2, 3, 4], [5, 6]), ([4, 5, 6], [7, 8, 9])]
    """
    total_window = train_window + val_window

    done_flag = False
    for start in range(0, len(dates), val_window):
        end = start + total_window

        # Look ahead to see if this is the last full window
        is_last_window = end + val_window > len(dates)

        if fold_incomplete and is_last_window:
            # For the last window, include all remaining data
            window = dates[start:]
            done_flag = True
        else:
            window = dates[start:end]

        if len(window) <= train_window:
            # If we can't make a full training window, we're done
            break

        train = window[:train_window]
        val = window[train_window:]

        yield train, val

        if done_flag:
            break
