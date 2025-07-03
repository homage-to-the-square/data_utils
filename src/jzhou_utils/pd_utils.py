import pandas as pd
import numpy as np

"""
    Df utils:
"""

def strip_excess_spaces_df(df: pd.DataFrame) -> pd.DataFrame:
    """
        Returns dataframe with leading + trailing spaces stripped for string columns
        - from gpt, but note that this has high mem usage + slow effectiveness
    """
    df_cleaned = df.copy()
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, str)).mean() > 0.1:
            df_cleaned[col] = df[col].str.rstrip()
    return df_cleaned


def str_to_float_df(df: pd.DataFrame) -> pd.DataFrame:
    """
        Try to convert all string columns into floats or ints, depending on pd.to_numeric 
    """
    df_converted = df.copy()
    for col in df_converted.columns:
        try:
            df_converted[col] = pd.to_numeric(df_converted[col], errors='raise')
        except Exception as e:
            pass  # Skip columns that can't be converted
    return df_converted

def format_size(size_bytes) -> str:
    """Convert bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:,.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:,.2f} PB"
    
def print_np_arr_mem_usage(arr: np.array) -> None:
    """Print memory usage of numpy array in human-readable format."""
    if not isinstance(arr, np.ndarray):
        print(f"Input is not a numpy array.")
        return
    size_bytes = arr.nbytes
    print(f"Array size: {format_size(size_bytes)}")