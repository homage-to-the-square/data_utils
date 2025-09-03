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

def cov_to_corr_and_var(cov: np.array):
    """
    Convert a covariance matrix to a correlation matrix and extract variances.

    Parameters:
        cov (np.ndarray): Covariance matrix (n x n)

    Returns:
        corr (np.ndarray): Correlation matrix (n x n)
        variances (np.ndarray): Variance vector (n,)
    """
    variances = np.diag(cov)
    stddev = np.sqrt(variances)
    outer_stddev = np.outer(stddev, stddev)
    
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        corr = cov / outer_stddev
        corr[outer_stddev == 0] = 0  # Set entries to 0 where stddev is zero
    
    return corr, variances

def corr_and_var_to_cov(corr, variances):
    """
    Convert a correlation matrix and variances to a covariance matrix.

    Parameters:
        corr (np.ndarray): Correlation matrix (n x n)
        variances (np.ndarray): Variance vector (n,)

    Returns:
        cov (np.ndarray): Covariance matrix (n x n)
    """
    stddev = np.sqrt(variances)
    outer_stddev = np.outer(stddev, stddev)
    cov = corr * outer_stddev
    return cov

def cosine_similarity(vec1, vec2) -> np.array:
    """
    Compute the cosine similarity between two vectors.
    
    Parameters:
        vec1, vec2 (array-like): Input vectors of equal length.
        
    Returns:
        float: Cosine similarity between vec1 and vec2.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    
    if norm_product == 0:
        return 0.0  # convention: similarity with a zero vector is 0
    
    return dot_product / norm_product
    
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