import pandas as pd
import numpy as np

def dataframe_to_latex_finance(df: pd.DataFrame, 
                      panel_title=None,
                      float_precision=4,
                      bold_max_per_row=False,
                      column_header_name="T",
                      table_width="\\textwidth",
                      position="ht!",
                      caption=None,
                      label=None,
                      include_table_env=True,
                      array_stretch=1.2,
                      tab_col_sep="8pt"):
    """
    Convert a pandas DataFrame table to professional LaTeX table formatting for finance journals.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame to convert
    panel_title : str, optional
        Title for the panel (e.g., "Panel A: 100 Portfolios Formed on Size and Book-to-Market")
    float_precision : int, default 4
        Number of decimal places for floating point numbers
    bold_max_per_row : bool, default False
        Whether to bold the maximum value in each row (excluding index)
    column_header_name : str, default "T"
        Name for the column header (appears above column names)
    table_width : str, default "\\textwidth"
        Width of the table (e.g., "\\textwidth", "0.8\\textwidth")
    position : str, default "ht!"
        Table position specifier
    caption : str, optional
        Table caption
    label : str, optional
        Table label for referencing
    include_table_env : bool, default True
        Whether to include the table environment wrapper
    array_stretch : float, default 1.2
        Row height multiplier
    tab_col_sep : str, default "8pt"
        Column separation distance
        
    Returns:
    --------
    str : Complete LaTeX table code
    """
    
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Generate column alignment - first column left, rest centered with auto-width
    num_data_cols = len(df.columns)
    column_alignment = f"@{{}}c|*{{{num_data_cols}}}{{>{{\\centering\\arraybackslash}}X}}@{{}}"
    
    # Start building LaTeX code
    latex_lines = []
    
    # Add top rule
    latex_lines.append("\\toprule")
    
    # Add panel title if provided
    if panel_title:
        colspan = len(df.columns) + 1  # +1 for index column
        # Format panel title without bold formatting
        if ":" in panel_title:
            # Split at colon but don't bold
            parts = panel_title.split(":", 1)
            formatted_title = f"{parts[0].strip()}: {parts[1].strip()}"
        else:
            formatted_title = panel_title
        
        latex_lines.append(f"\\multicolumn{{{colspan}}}{{c}}{{\\makecell{{{formatted_title}}}}} \\\\")
        latex_lines.append("\\midrule")
    
    # Create column header line with diagbox
    header_line = f"\\diagbox{{Method}}{{${column_header_name}$}}"
    for col in df.columns:
        header_line += f" & {col}"
    header_line += " \\\\"
    latex_lines.append(header_line)
    latex_lines.append("\\midrule")
    
    # Process each row
    for idx, row in df_copy.iterrows():
        row_values = []
        numeric_values = []
        
        # Convert values to strings with proper formatting
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                row_values.append("")
                numeric_values.append(np.nan)
            elif isinstance(val, (int, float, np.number)):
                formatted_val = f"{val:.{float_precision}f}"
                row_values.append(formatted_val)
                numeric_values.append(val)
            else:
                row_values.append(str(val))
                numeric_values.append(np.nan)
        
        # Find maximum value for bolding if requested
        max_idx = None
        if bold_max_per_row and len(numeric_values) > 0:
            valid_nums = [x for x in numeric_values if not pd.isna(x)]
            if valid_nums:
                max_val = max(valid_nums)
                max_idx = next(i for i, x in enumerate(numeric_values) if x == max_val)
        
        # Build row string - no bolding applied
        row_str = str(idx)  # Index column
        for i, val_str in enumerate(row_values):
            row_str += f" & {val_str}"
        row_str += " \\\\"
        
        latex_lines.append(row_str)
    
    # Add bottom rule
    latex_lines.append("\\bottomrule")
    
    # Join all lines with proper indentation
    latex_content = "\n        ".join(latex_lines)
    
    # Build the complete table
    if include_table_env:
        table_parts = []
        table_parts.append(f"\\begin{{table}}[{position}]")
        table_parts.append("    \\centering")
        table_parts.append(f"    \\renewcommand{{\\arraystretch}}{{{array_stretch}}}")
        table_parts.append(f"    \\setlength{{\\tabcolsep}}{{{tab_col_sep}}}")
        table_parts.append(f"    \\begin{{tabularx}}{{{table_width}}}{{{column_alignment}}}")
        table_parts.append(f"        {latex_content}")
        table_parts.append("    \\end{tabularx}")
        
        if caption:
            table_parts.append(f"    \\caption{{{caption}}}")
        if label:
            table_parts.append(f"    \\label{{{label}}}")
            
        table_parts.append("\\end{table}")
        
        return "\n".join(table_parts)
    else:
        # Return just the tabularx environment
        return f"""\\begin{{tabularx}}{{{table_width}}}{{{column_alignment}}}
        {latex_content}
\\end{{tabularx}}"""