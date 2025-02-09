import pandas as pd

def verify_csv_integrity(file_path):
    # Try to load the file to check for syntax or formatting errors
    try:
        df = pd.read_csv(file_path)
    except pd.errors.ParserError as e:
        print(f"Parsing Error: {e}")
        return False
    except Exception as e:
        print(f"Error loading file: {e}")
        return False

    # Verify that the number of columns is consistent across all rows
    num_columns = len(df.columns)
    for idx, row in enumerate(df.iterrows()):
        if len(row[1]) != num_columns:  # row[1] is the row content
            print(f"Error at Line {idx }: Inconsistent number of columns")
            print(f"Problematic Row: {row[1].tolist()}")
            return False

    # Verify header integrity (if headers are as expected)
    expected_columns = ['Details', 'Posting Date', 'Description', 'Amount', 'Type', 'Balance', 'Check or Slip #']
    if list(df.columns) != expected_columns:
        print(f"Error: Header mismatch")
        print(f"Expected header: {expected_columns}")
        print(f"Actual header: {df.columns.tolist()}")
        return False

    # Check if required columns have valid data types (e.g., Amount should be numeric)
    invalid_amount_rows = df[~df['Amount'].apply(pd.to_numeric, errors='coerce').notna()]
    if not invalid_amount_rows.empty:
        print("Error: 'Amount' column contains invalid data")
        for idx, row in invalid_amount_rows.iterrows():
            # Ensure idx is treated as an integer and converted to string for concatenation
            print(f"Error at Line {idx }: Invalid 'Amount' value")
            print(f"Problematic Row: {row.tolist()}")
            print(f"Invalid 'Amount' Value: {row['Amount']}")
        return False

    # Check for empty rows or missing values in important columns (Amount, Description, Posting Date)
    missing_values = df[['Amount', 'Description', 'Posting Date']].isnull()
    if missing_values.any().any():
        print("Error: Missing values in important columns")
        for idx, row in missing_values[missing_values.any(axis=1)].iterrows():
            # Ensure idx is treated as an integer and converted to string for concatenation
            print(f"Error at Line {idx }: Missing value(s) in the row")
            print(f"Problematic Row: {df.iloc[idx].tolist()}")
        return False

    print("File integrity verified successfully!")
    return True

# Example usage:
file_path = 'Chase0106_Activity_20250205.CSV'
if verify_csv_integrity(file_path):
    print("File is ready for processing.")
else:
    print("File has integrity issues. Please check the logs above.")
