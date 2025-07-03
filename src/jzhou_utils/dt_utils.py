import pandas as pd
import datetime as dt
from typing import Union

def YYYYMM_to_date(s: pd.Series) -> pd.Series:
    """
        converts series of integers of form YYYYMM into dates
    """
    return pd.to_datetime(s.astype(str), format='%Y%m').dt.date

def date_id_to_date(date_id: Union[int, pd.Series]):
    if isinstance(date_id, int):
        return dt.datetime.strptime(str(date_id), '%Y%m%d').date()
    else:
        return pd.to_datetime(date_id.astype(str), format='%Y%m%d').dt.date

def date_to_date_id(date: dt.date) -> int:
    return int(date.strftime('%Y%m%d'))

def get_friday_of_isocalendar(iso_year, iso_week):
    # Get the first day of the ISO week
    first_day_of_week = dt.date(iso_year, 1, 1) + dt.timedelta(weeks=iso_week-1)
    
    # Adjust to the correct day of the week (Friday is 4)
    # `first_day_of_week.weekday()` gives the weekday of the first day of the ISO week.
    # We need to adjust to make sure we get the Friday of that week.
    days_to_friday = (4 - first_day_of_week.weekday()) % 7
    friday = first_day_of_week + dt.timedelta(days=days_to_friday)
    return friday
