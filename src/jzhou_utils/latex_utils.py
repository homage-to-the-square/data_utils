import numpy as np
import pandas as pd


def dataframe_to_latex(
    df,
    panel_title=None,
    float_precision=4,
    bold_max_per_row=False,
    bold_max_per_column=False,
    column_header_name="T",
    secondary_header_name: str = f'\\beta',
    table_width="\\textwidth",
    position="ht!",
    caption=None,
    label=None,
    include_table_env=True,
    array_stretch=1.2,
    tab_col_sep="8pt",
):
    """
    Convert a pandas DataFrame to professional LaTeX table formatting.
    Supports both regular and MultiIndex columns (of 2 multi-index).

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
    bold_max_per_column : bool, default False
        Whether to bold the maximum value in each column
    column_header_name : str, default "T"
        Name for the column header (appears above column names)
    secondary_header_name: str
        Name for the second column header, if df is multiindex with 2 columns    
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

    # Check if we have MultiIndex columns
    is_multiindex = isinstance(df.columns, pd.MultiIndex)

    # Pre-calculate column maxima if bold_max_per_column is True
    column_max_indices = {}
    if bold_max_per_column:
        for col_idx, col in enumerate(df.columns):
            numeric_values = []
            row_indices = []
            for row_idx, val in enumerate(df[col]):
                if pd.notna(val) and isinstance(val, (int, float, np.number)):
                    numeric_values.append(val)
                    row_indices.append(row_idx)
            
            if numeric_values:
                max_val = max(numeric_values)
                max_row_idx = row_indices[numeric_values.index(max_val)]
                column_max_indices[col_idx] = max_row_idx

    if is_multiindex:
        # Handle MultiIndex columns
        num_data_cols = len(df.columns)

        # Build alignment string with vertical lines between level 0 groups
        alignment_parts = ["@{}c|"]  # Start with the method column
        level_0_values = df.columns.get_level_values(0).unique()
        col_idx = 0
        for i, level_0_val in enumerate(level_0_values):
            count = sum(1 for col in df.columns if col[0] == level_0_val)
            
            # Add columns for this group
            for j in range(count):
                alignment_parts.append("c")
                col_idx += 1
            
            # Add vertical line after each group except the last
            if i < len(level_0_values) - 1:
                alignment_parts.append("|")
        
        alignment_parts.append("@{}")  # End
        column_alignment = "".join(alignment_parts)

        # Get unique values from each level
        level_0_values = df.columns.get_level_values(0).unique()
        level_1_values = df.columns.get_level_values(1).unique()

        # Start building LaTeX code
        latex_lines = []

        # Add top rule
        latex_lines.append("\\toprule")

        # Add panel title if provided
        if panel_title:
            colspan = len(df.columns) + 1  # +1 for index column
            # Format panel title
            if ":" in panel_title:
                parts = panel_title.split(":", 1)
                formatted_title = f"{parts[0].strip()}: {parts[1].strip()}"
            else:
                formatted_title = panel_title

            latex_lines.append(
                f"\\multicolumn{{{colspan}}}{{c}}{{{formatted_title}}} \\\\"
            )
            latex_lines.append("\\midrule")

        # Create the diagonal header
        diagbox_content = f"\\diagbox{{Method}}{{${secondary_header_name}, {column_header_name}$}}"

        # Create top header row with level 0 values
        header_line_1 = diagbox_content
        for level_0_val in level_0_values:
            # Count how many columns this level 0 value spans
            count = sum(1 for col in df.columns if col[0] == level_0_val)
            if level_0_val != level_0_values[-1]:
                header_line_1 += (
                    f" & \\multicolumn{{{count}}}{{c|}}{{${secondary_header_name} = {level_0_val}$}}"
                )
            else:
                header_line_1 += (
                    f" & \\multicolumn{{{count}}}{{c}}{{${secondary_header_name} = {level_0_val}$}}"
                )
        header_line_1 += " \\\\"
        latex_lines.append(header_line_1)

        # Add cmidrule for the level 0 headers
        cmidrule_parts = []
        col_start = 2  # Start from column 2 (after the diagonal box)
        for level_0_val in level_0_values:
            count = sum(1 for col in df.columns if col[0] == level_0_val)
            col_end = col_start + count - 1
            cmidrule_parts.append(f"\\cmidrule(lr){{{col_start}-{col_end}}}")
            col_start = col_end + 1
        latex_lines.append(" ".join(cmidrule_parts))

        # Create second header row with level 1 values
        header_line_2 = ""
        for i, (level_0_val, level_1_val) in enumerate(df.columns):
            if i == 0:
                header_line_2 += f" & {level_1_val}"
            else:
                header_line_2 += f" & {level_1_val}"
        header_line_2 += " \\\\"
        latex_lines.append(header_line_2)
        latex_lines.append("\\midrule")

    else:
        # Handle regular columns (original code)
        num_data_cols = len(df.columns)
        column_alignment = (
            f"@{{}}c|*{{{num_data_cols}}}{{>{{\\centering\\arraybackslash}}X}}@{{}}"
        )

        # Start building LaTeX code
        latex_lines = []

        # Add top rule
        latex_lines.append("\\toprule")

        # Add panel title if provided
        if panel_title:
            colspan = len(df.columns) + 1  # +1 for index column
            if ":" in panel_title:
                parts = panel_title.split(":", 1)
                formatted_title = f"{parts[0].strip()}: {parts[1].strip()}"
            else:
                formatted_title = panel_title

            latex_lines.append(
                f"\\multicolumn{{{colspan}}}{{c}}{{\\makecell{{{formatted_title}}}}} \\\\"
            )
            latex_lines.append("\\midrule")

        # Create column header line with diagbox
        header_line = f"\\diagbox{{Method}}{{${column_header_name}$}}"
        for col in df.columns:
            header_line += f" & {col}"
        header_line += " \\\\"
        latex_lines.append(header_line)
        latex_lines.append("\\midrule")

    # Process each row (same for both MultiIndex and regular)
    for row_idx, (idx, row) in enumerate(df_copy.iterrows()):
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
        row_max_idx = None
        if bold_max_per_row and len(numeric_values) > 0:
            valid_nums = [x for x in numeric_values if not pd.isna(x)]
            if valid_nums:
                max_val = max(valid_nums)
                row_max_idx = next(i for i, x in enumerate(numeric_values) if x == max_val)

        # Build row string
        row_str = str(idx)  # Index column
        for i, val_str in enumerate(row_values):
            should_bold = False
            
            # Check if should bold for row maximum
            if bold_max_per_row and i == row_max_idx and val_str:
                should_bold = True
            
            # Check if should bold for column maximum
            if bold_max_per_column and i in column_max_indices and column_max_indices[i] == row_idx and val_str:
                should_bold = True
            
            if should_bold:
                row_str += f" & \\textbf{{{val_str}}}"
            else:
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

        # Wrap tabular in resizebox to fit table width
        table_parts.append(f"    \\resizebox{{{table_width}}}{{!}}{{%")

        # Use appropriate table environment
        if is_multiindex:
            table_parts.append(f"        \\begin{{tabular}}{{{column_alignment}}}")
        else:
            table_parts.append(
                f"        \\begin{{tabularx}}{{{table_width}}}{{{column_alignment}}}"
            )

        table_parts.append(f"            {latex_content}")

        if is_multiindex:
            table_parts.append("        \\end{tabular}")
        else:
            table_parts.append("        \\end{tabularx}")

        table_parts.append("    }%")  # Close resizebox

        if caption:
            table_parts.append(f"    \\caption{{{caption}}}")
        if label:
            table_parts.append(f"    \\label{{{label}}}")

        table_parts.append("\\end{table}")

        return "\n".join(table_parts)
    else:
        # Return just the table environment wrapped in resizebox
        if is_multiindex:
            return f"""\\resizebox{{{table_width}}}{{!}}{{%
\\begin{{tabular}}{{{column_alignment}}}
        {latex_content}
\\end{{tabular}}%
}}"""
        else:
            return f"""\\resizebox{{{table_width}}}{{!}}{{%
\\begin{{tabularx}}{{{table_width}}}{{{column_alignment}}}
        {latex_content}
\\end{{tabularx}}%
}}"""