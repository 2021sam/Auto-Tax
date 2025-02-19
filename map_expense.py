import os
import pandas as pd
from tkinter import filedialog, Tk

def import_data(transaction_file_name):
    print('Import Data:')
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

    # Print the DataFrame structure
    # print_df_structure(df)
    return df

def preprocess_file(df):
    """Load and preprocess the CSV file into DataFrame 1 and then create DataFrame 2."""
    print('Pre Process File:')
    
    # Step 2: Create a new DataFrame 2 with the desired column headings
    desired_columns = ["Details", "Posting Date", "Description", "Amount", "Type", "Balance", "Check"]
    
    # Step 3: Initialize DataFrame 2 with empty columns
    df_2 = pd.DataFrame(columns=desired_columns)
    print(df_2.columns.to_list())

    # Step 4: Create a mapping structure to map columns from DataFrame 1 to DataFrame 2
    column_mapping = {
        "Date": "Posting Date",       # Map Date to Posting Date
        "Description": "Description", # Direct mapping
    }

    # Step 5: Populate DataFrame 2 with values from DataFrame 1 using the mapping
    for original_col, target_col in column_mapping.items():
        print(f' original_col: {original_col}, target_col: {target_col}')
        if original_col in df.columns:
            df_2[target_col] = df[original_col]
        else:
            print(f"Warning: {original_col} not found in DataFrame 1.")

    # Step 6: Handle the Amount column by checking if there's a Debit value
    for i, row in df.iterrows():
        if pd.notnull(row['Debit']):  # If Debit has a value
            df_2.at[i, 'Amount'] = row['Debit']
        elif pd.notnull(row['Credit']):  # If Debit is empty, use Credit
            df_2.at[i, 'Amount'] = -row['Credit']  # Make Credit negative for Amount

    # Print the final structure and check if rows are added
    print("df_2 structure after preprocessing:")
    # print_df_structure(df_2)

    return df_2


def map(df, file_coa):
    """Perform the mapping of COA to the global DataFrame."""
    print('')
    print('map')
    
    if df is None:
        print("Error: The transaction data has not been preprocessed yet.")
        return None, None
    
    print(f'Mapping transactions with COA file: {file_coa}')
    
    # Read the chart of accounts (COA) file
    try:
        coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
        print(f"COA file loaded successfully: {file_coa}")
        # print_df_structure(coa)
    except Exception as e:
        print(f"Error loading COA file {file_coa}: {e}")
        return None, None
    
    # Initialize a variable to track how many rows do not match COA
    mia = 0
    
    # Iterate through each row in the DataFrame
    for i, row in df.iterrows():
        match = False

        # Perform the mapping based on the COA description
        for j, coa_row in coa.iterrows():
            if coa.loc[j, 'DESCRIPTION'] in df.loc[i, 'Description']:
                match = True
                df.loc[i, 'KEY'] = coa.loc[j, 'EXPENSE']
        
        # If no match found, increment 'mia'
        if not match:
            mia += 1
            print(i, df.loc[i, 'KEY'], df.loc[i, 'Description'], df.loc[i, 'Amount'])

    print(f'MIA = {mia}')
    
    return mia, df


def group_expenses(df):
    """Group the expenses based on the KEY column."""
    
    # Group the transactions by KEY and sum the amounts
    x = df.groupby(['KEY'])[['Amount']]
    y = x.sum()
    
    # Read the Chart of Accounts Key (COA) file
    key = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', 'coa', 'Chart_Of_Accounts_Key.txt'), encoding='latin1', thousands=',')
    
    print('********************************** KEY')
    # key = key[key['KEY'] != 0]
    # key = key[key['KEY'] != 0]  # Filter out the row with KEY == 0
    print_df_structure(key)
    # Merge the grouped data with the COA key based on the KEY column
    e = pd.merge(key, y, how='outer', on='KEY')
    print('.................................. group_expenses')
    # print_df_structure(e)
    expense_sum = e[e['Amount'].notna()]    #: This line filters out rows where the Amount is NaN.



    print('expense_sum:')
    print(expense_sum.index)
    
    # print(f"key['0'] value: {key.iloc[0]}")  # Checking the first row

    # print("First few rows of 'key':")
    # print(key.head())

    # print("First few rows of 'expense_sum':")
    # print(expense_sum.head())


    # expense_sum = expense_sum.drop(index=key[0])
    # If key['0'] is an integer index (e.g., 0)
    # expense_sum = expense_sum.drop(index=int(key['0']), errors='ignore')


    return expense_sum


def print_df_structure(df):
    print('**************************  DATAFRAME STRUCTURE')
    print(df.columns.to_list())
    print('.')
    print('head:')
    print(df.head())
    print('.')
    print('First Row (iloc):')
    print(df.iloc[0])
    print('.')
    print('First Row & First Column (iloc[0, 0]):')
    print(df.iloc[0, 0])


def save_expenses_to_csv(expense_sum):
    """Save the expenses DataFrame to a CSV file."""
    save_path = os.path.join(os.path.dirname(__file__), "Expense.csv")
    
    print("Your tax file is saved to the following location:")
    print(save_path)
    
    # Save the DataFrame to the CSV file
    expense_sum.to_csv(save_path)
    print("File saved successfully.")



# Example of running the code
if __name__ == "__main__":
    # Relative path to the COA file
    file_coa = os.path.join(os.path.dirname(__file__), 'data', 'coa', 'Chart_Of_Accounts_Mappings.txt')

    # Provide path to the transaction file here
    transaction_file_name = os.path.join(os.path.dirname(__file__), 'data', 'transactions', 'Chase0106_Activity_20250205.CSV')
    df = import_data(transaction_file_name)

    # Check if both 'Debit' and 'Credit' columns are present
    if 'Debit' in df.columns and 'Credit' in df.columns:
        df = preprocess_file(df)
        print('**************************  PRE PROCESSING IS COMPLETE')

    df['KEY'] = None  # Add a new column called 'KEY' with a default value
    
    # Call the map function to map the transactions with the COA
    mia, mapped_transactions = map(df, file_coa)
    print(f"Warning: There are {mia} transactions MIA.")

    expense_sum = group_expenses(mapped_transactions)
    save_expenses_to_csv(expense_sum)
    