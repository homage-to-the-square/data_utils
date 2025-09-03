import pandas as pd
import sqlite3


def sqlite_type_to_pd_dtype(sqltype):
    """Map SQLite types to pandas/numpy dtypes."""
    sqltype = sqltype.upper()
    if 'INT' in sqltype:
        return 'Int64'       # pandas nullable integer
    if 'REAL' in sqltype or 'FLOA' in sqltype or 'DOUB' in sqltype:
        return 'float64'
    if 'TEXT' in sqltype or 'CHAR' in sqltype or 'CLOB' in sqltype:
        return 'string'
    if 'BLOB' in sqltype:
        return 'object'
    # NUMERIC and others: fallback to string
    return 'string'


def safe_append_sqlite(db_path: str, table: str, df: pd.DataFrame, chunksize: int = 1000):
    """
    Safely append a DataFrame to an existing SQLite table, checking/casting types as needed.

    - DataFrame must contain at least all table columns.
    - Extra DataFrame columns not in table are ignored.
    - Missing required table columns raises ValueError.
    - Existing rows (by primary key) in the db are NOT overwritten.
    - Dtypes are automatically checked and cast.
    - Works for single and composite primary keys.
    """
    conn = sqlite3.connect(db_path)
    try:
        # Get table schema and expected types
        schema = pd.read_sql(f"PRAGMA table_info({table});", conn)
        table_cols = schema["name"].tolist()
        col_types = dict(zip(schema["name"], schema["type"]))

        # Check for missing columns
        missing_cols = set(table_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"DataFrame is missing required columns: {missing_cols}")

        # Infer PK columns
        pk_cols = schema[schema['pk'] > 0]['name'].tolist()
        if not pk_cols:
            raise ValueError("No primary key found in table schema.")

        # Get existing PKs from database
        query_cols = ', '.join([f'"{col}"' for col in pk_cols])
        existing_rows = pd.read_sql(f"SELECT {query_cols} FROM {table};", conn)

        # Filter df to new PKs only
        if len(pk_cols) == 1:
            pk = pk_cols[0]
            df_new = df[~df[pk].isin(existing_rows[pk])]
        else:
            df_merge = df.merge(existing_rows, on=pk_cols, how='left', indicator=True)
            df_new = df_merge[df_merge['_merge'] == 'left_only'].drop(columns=['_merge'])

        # Align and cast DataFrame
        df_aligned = df_new[table_cols].copy()
        for col, sqlite_type in col_types.items():
            pd_type = sqlite_type_to_pd_dtype(sqlite_type)
            try:
                df_aligned[col] = df_aligned[col].astype(pd_type)
            except Exception as e:
                raise TypeError(
                    f"Failed to cast column '{col}' to '{pd_type}' for SQLite type '{sqlite_type}'. "
                    f"Error: {e}\n"
                    f"Problematic values:\n{df_aligned[col]}"
                )

        # Append filtered, aligned DataFrame to table
        if not df_aligned.empty:
            df_aligned.to_sql(table, conn, if_exists="append", index=False, chunksize=chunksize, method="multi")

    finally:
        conn.close()