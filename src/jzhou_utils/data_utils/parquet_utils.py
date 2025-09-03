import os
from pathlib import Path
import pandas as pd

def safe_save_parquet(df: pd.DataFrame, file_path: str, **kwargs) -> None:
    """
    Safely save a DataFrame to a parquet file, creating directories if needed.
    Will fail if the target file already exists to prevent overwrites.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame to save
    file_path : str or Path
        Path where the parquet file should be saved
    **kwargs : dict
        Additional keyword arguments to pass to df.to_parquet()
    
    Returns:
    --------
    Path
        The path where the file was saved
    
    Raises:
    -------
    FileExistsError
        If the target file already exists
    Exception
        Re-raises any other exception that occurs during the save process
    """
    try:
        # Convert to Path object for easier manipulation
        path = Path(file_path)
        
        # Check if file already exists
        if path.exists():
            raise FileExistsError(f"File already exists: {path}")
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the DataFrame to parquet
        df.to_parquet(path, **kwargs)
        
        print(f"Successfully saved DataFrame to {path}")
        return path
        
    except Exception as e:
        print(f"Error saving DataFrame to {file_path}: {str(e)}")
        raise
