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

# Extract the column names from the first row
header_row = header_row.iloc[0].tolist()  # Get the first row as a list of column names

# Check number of columns in header_row and the DataFrame
print(f"Header row has {len(header_row)} columns")
print(f"DataFrame has {len(header_row)} columns before setting the columns")

print('read data:')
# Read the CSV file without a header, skip the first row (skiprows=1)
try:
    # Read the CSV file with error handling to skip bad rows
    df = pd.read_csv(transaction_file_name, header=None, skiprows=1, on_bad_lines='skip')
    print("Data read successfully!")
except Exception as e:
    print(f"Error reading file: {e}")

# Verify the number of columns in df
print(f"DataFrame has {df.shape[1]} columns")

# Drop the last column if it doesn't match the header (extra column)
if len(df.columns) > len(header_row):
    df = df.iloc[:, :-1]  # Remove the last column if it exceeds the header length

# Set the column names from the header_row list
df.columns = header_row


# Add a new column called 'KEY' with a default value or calculated values
df['KEY'] = None  # You can replace 'default_value' with the value you want to assign to this column


# Print the DataFrame structure
print_df_structure(df)

