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
    print('First Row & First Column (iloc[0, 0]:')
    # Print the value of the first row and first column (i.e., value at (0, 0))
    print(df.iloc[0, 0])

    # # Iterate over all columns in the DataFrame
    # for column in df.columns:
    #     print(f"Column: {column}")
    #     print(df[column].head())  # Print first 5 rows of each column
    #     print()  # Print a blank line for separation

        # for v in df[column]:
        #     print(v)





transaction_file_name = "Chase0106_Activity_20250205.CSV"
# Read the actual header row (first row) separately using nrows=1
header_row = pd.read_csv(transaction_file_name, header=None, nrows=1)
# Set the correct header from the first row
header_row.columns = header_row.iloc[0]
# print_df_structure(header_row)

print('read data:')
# Read the CSV file without a header (header=None) to get the number of columns

try:
    # Read the CSV file with error handling to skip bad rows
    df = pd.read_csv(transaction_file_name, header=None, skiprows=1, on_bad_lines='skip')  # or error_bad_lines=False for older pandas versions
    print("Data read successfully!")
except Exception as e:
    print(f"Error reading file: {e}")


df.columns = header_row  # Set the first row as column names
# df = df[1:].reset_index(drop=True)  # Remove the first row from the data


print_df_structure(df)

# # Now assign the header row to the DataFrame
# chase_df.columns = header_row.iloc[0]

# # Optionally, remove the header row from the data (if it was read as part of the DataFrame)
# chase_df = chase_df[1:].reset_index(drop=True)

# Check the result
# print(chase_df.head())
