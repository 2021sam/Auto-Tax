import pandas as pd

def print_df_structure(df):
    print('**************************  DATAFRAME STRUCTURE')
    print(df.columns.to_list())
    print('.')
    print('head:')
    print(df.head())
    print('.')
    print('First Row (iloc):')
    print(df.iloc[0])
    print('First Row & First Column (iloc[0, 0]):')
    print(df.iloc[0, 0])

# File name
transaction_file_name = "Chase0106_Activity_20250205.CSV"

# Read the actual header row (first row) separately using nrows=1
header_row = pd.read_csv(transaction_file_name, header=None, nrows=1)
print_df_structure(header_row)

# Extract column names from the first row
header_row = header_row.iloc[0].tolist()  # Get the first row as a list
print(len(header_row))





print('read data:')
# Read the CSV file without a header, skip the first row (skiprows=1)
try:
    # Read the CSV file with error handling to skip bad rows
    df = pd.read_csv(transaction_file_name, header=None, skiprows=1, on_bad_lines='skip')
    print("Data read successfully!")
except Exception as e:
    print(f"Error reading file: {e}")

# Set the column names from the header_row list
df.columns = header_row

# Print the DataFrame structure
print_df_structure(df)
