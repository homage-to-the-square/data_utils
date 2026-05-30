import os
import math
import pandas as pd
import numpy as np
from typing import List, Dict

def calculate_final_grades(
    csv_path: str, 
    hw_prefixes: List[str], 
    midterm_prefix: str, 
    final_prefix: str, 
    weights: Dict[str, float],
    name_cols: List[str] = ['First Name', 'Last Name'],
    drop_lowest_hw: bool = True
) -> pd.DataFrame:
    """
    Reads a gradebook CSV, validates schemas/weights, and computes final student grades.

    This function processes assignment columns dynamically based on text prefixes,
    accounts for maximum possible points per assignment, handles missing data by 
    defaulting to zero, and can optionally drop the single lowest homework score 
    by calculating which omission yields the highest overall percentage.

    Parameters:
    -----------
    csv_path : str
        The file path to the source gradebook CSV.
        Must contain 'SID', 'Email', and columns defined by `name_cols`.
    hw_prefixes : list of str
        The column header prefixes for homework scores. For each prefix, the CSV 
        must also contain a corresponding "{prefix} - Max Points" column.
    midterm_prefix : str
        The column header prefix for the midterm exam score. Requires a 
        corresponding "{midterm_prefix} - Max Points" column.
    final_prefix : str
        The column header prefix for the final exam score. Requires a 
        corresponding "{final_prefix} - Max Points" column.
    weights : dict of str -> float
        A dictionary containing keys 'hw', 'midterm', and 'final'. 
        The float values must sum up to exactly 1.0 (within a 1e-5 tolerance).
    name_cols : list of str, default ['First Name', 'Last Name']
        Columns used to identify student names. Used for sorting the output.
    drop_lowest_hw : bool, default True
        If True, drops the single homework assignment prefix that maximizes the 
        student's cumulative homework percentage. If False, retains all homeworks.

    Returns:
    --------
    pd.DataFrame
        A processed DataFrame containing:
        - Student identifying info ('SID', 'Email', and `name_cols`)
        - Individual percentage scores for each homework assignment
        - Total cumulative homework percentage ('Total HW (%)')
        - Identifiers for dropped homeworks ('Dropped HW', or "None")
        - Exam percentages ('Midterm (%)', 'Final (%)')
        - Weighted final grades ('Overall Grade (%)')
        The rows are sorted in ascending order by the reverse sequence of `name_cols`.

    Raises:
    -------
    FileNotFoundError
        If the file at `csv_path` does not exist.
    ValueError
        If weights do not total 1.0, the CSV is empty, or mandatory columns are missing.
    """
    
    # =========================================================================
    # ERROR HANDLING & VALIDATION
    # =========================================================================
    
    # 1. Check if file exists
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Could not find the file at path: '{csv_path}'. Please check the file path.")
    
    # 2. Check if weights sum to 1.0
    total_weight = sum(weights.values())
    if not math.isclose(total_weight, 1.0, rel_tol=1e-5):
        raise ValueError(f"The weights must sum up to exactly 1.0. Your current weights sum to: {total_weight}")

    # Load the CSV
    df = pd.read_csv(csv_path)
    
    # 3. Check if the dataframe is empty
    if df.empty:
        raise ValueError("The provided CSV file is empty. No student data found.")

    # Generate exact expected column names based on user-provided prefixes
    hw_score_cols = [f"{prefix}" for prefix in hw_prefixes]
    hw_max_cols = [f"{prefix} - Max Points" for prefix in hw_prefixes]
    midterm_max_col = f"{midterm_prefix} - Max Points"
    final_max_col = f"{final_prefix} - Max Points"
    
    # 4. Check for missing structural or grade columns
    expected_columns = (
        name_cols +
        ['SID', 'Email', midterm_prefix, midterm_max_col, final_prefix, final_max_col] + 
        hw_score_cols + 
        hw_max_cols
    )
    
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(
            "The following required columns are missing from the CSV:\n"
            f"  - {', '.join(missing_cols)}\n"
            "Please check your prefixes and ensure the CSV headers match exactly."
        )

    # =========================================================================
    # GRADE CALCULATION LOGIC
    # =========================================================================
    
    # Clean incoming data: treat missing assignments (NaNs) as zero scores
    df[hw_score_cols] = df[hw_score_cols].fillna(0)
    df[midterm_prefix] = df[midterm_prefix].fillna(0)
    df[final_prefix] = df[final_prefix].fillna(0)

    # Initialize the output DataFrame with identifying demographic information
    out_df = pd.DataFrame()
    for c in name_cols:
        out_df[c] = df[c]
    out_df['SID'] = df['SID']
    out_df['Email'] = df['Email']
    
    # Vectorized calculation of individual homework percentages
    for score_col, max_col in zip(hw_score_cols, hw_max_cols):
        # Prevent division by zero if max points are configured as 0
        out_df[f'{score_col} (%)'] = np.where(df[max_col] > 0, (df[score_col] / df[max_col]) * 100, 0)

    # Compile overall homework score configurations using row-by-row analysis
    if drop_lowest_hw:
        def get_hw_score(row):
            best_score_pct = -1
            dropped_hw = None
            
            # Map exact scores and max points to their specific prefix to decouple from column index ordering
            scores = {prefix: row[prefix] for prefix in hw_prefixes}
            maxes = {prefix: row[f"{prefix} - Max Points"] for prefix in hw_prefixes}
            
            # Simulate dropping each homework prefix sequentially to find the mathematically optimal drop
            for drop_target in hw_prefixes:
                sum_kept_scores = 0
                sum_kept_maxes = 0
                
                for prefix in hw_prefixes:
                    if prefix != drop_target:
                        sum_kept_scores += scores[prefix]
                        sum_kept_maxes += maxes[prefix]
                
                current_pct = (sum_kept_scores / sum_kept_maxes) if sum_kept_maxes > 0 else 0
                
                if current_pct > best_score_pct:
                    best_score_pct = current_pct
                    dropped_hw = drop_target
                    
            return pd.Series([best_score_pct * 100, dropped_hw])
    else:
        def get_hw_score(row):
            scores = row[hw_score_cols].values
            maxes = row[hw_max_cols].values
            
            sum_scores = np.sum(scores)
            sum_maxes = np.sum(maxes)
            
            current_pct = (sum_scores / sum_maxes) if sum_maxes > 0 else 0
            return pd.Series([current_pct * 100, "None"])

    # Apply cumulative homework calculations across rows
    out_df[['Total HW (%)', 'Dropped HW']] = df.apply(get_hw_score, axis=1)
    
    # Vectorized calculation for Exam scores
    out_df['Midterm (%)'] = np.where(df[midterm_max_col] > 0, (df[midterm_prefix] / df[midterm_max_col]) * 100, 0)
    out_df['Final (%)'] = np.where(df[final_max_col] > 0, (df[final_prefix] / df[final_max_col]) * 100, 0)
    
    # Compute final weighted class standing
    out_df['Overall Grade (%)'] = (
        (out_df['Total HW (%)'] * weights['hw']) +
        (out_df['Midterm (%)'] * weights['midterm']) +
        (out_df['Final (%)'] * weights['final'])
    )
    
    # Standardize precision by rounding numerical stats to 2 decimal places
    numeric_cols = out_df.select_dtypes(include=[np.number]).columns
    out_df[numeric_cols] = out_df[numeric_cols].round(2)

    # Sort data by student naming preferences (reversed list slice) and normalize index structure
    out_df = out_df.sort_values(by=name_cols[::-1]).reset_index(drop=True)
    return out_df