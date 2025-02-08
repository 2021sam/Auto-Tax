import os
import pandas as pd
from tkinter import filedialog, Tk


# Global variable to store the preprocessed DataFrame
chase_df_2 = None

def preprocess_file(transaction_file_name):
    """Load and preprocess the CSV file into DataFrame 1 and then create DataFrame 2."""
    global chase_df_2
    
    print(f'Preprocessing file: {transaction_file_name}')
    try:
        # Step 1: Import the original file into DataFrame 1 (chase_df)
        chase_df = pd.read_csv(transaction_file_name)  # Don't skip any rows
        print(chase_df.columns.to_list())
        print(chase_df.tail())
        print(f"File loaded successfully: {transaction_file_name}")
        
        # Print the column names to debug (with trimming)
        print("Columns in the loaded file:", chase_df.columns)

        # Trim any extra spaces from column names
        chase_df.columns = chase_df.columns.str.strip()

        # Step 2: Create a new DataFrame 2 with the desired column headings
        desired_columns = ["Details", "Posting Date", "Description", "Amount", "Type", "Balance", "Check", "KEY"]
        
        # Step 3: Initialize DataFrame 2 (chase_df_2) with empty columns
        chase_df_2 = pd.DataFrame(columns=desired_columns)
        print(chase_df_2.columns.to_list())
        # Step 4: Create a mapping structure to map columns from DataFrame 1 to DataFrame 2
        column_mapping = {
            "Date": "Posting Date",       # Map Date to Posting Date
            "Description": "Description", # Direct mapping
            "Debit": "Amount",            # Debit becomes Amount
            "Credit": "Amount",           # Credit becomes Amount (negative)
        }
        
        # Step 5: Populate DataFrame 2 with values from DataFrame 1 using the mapping
        for original_col, target_col in column_mapping.items():
            if original_col in chase_df.columns:
                chase_df_2[target_col] = chase_df[original_col]
            else:
                print(f"Warning: {original_col} not found in DataFrame 1.")

        # Step 6: Calculate the 'Amount' column by combining 'Debit' and 'Credit'
        chase_df_2['Amount'] = chase_df_2['Debit'] - chase_df_2['Credit']
        
        # Step 7: Handle missing 'KEY' values and fill with 0
        chase_df_2['KEY'] = chase_df_2['KEY'].fillna(0)
        
        # Step 8: Add handling for 'Check' (if applicable) - You might want to handle 'Check' or 'Slip #' as required
        chase_df_2['Check'] = chase_df_2.get('Check', 'N/A')  # If there's no Check, default to 'N/A'
        
        print("Preprocessing complete.")
        print("First few rows of chase_df_2:")
        print(chase_df_2.head())  # Display first few rows of the new DataFrame 2
        
        return chase_df_2
    
    except Exception as e:
        print(f"Error processing file {transaction_file_name}: {e}")
        return None


def map(file_coa):
    """Perform the mapping of COA to the global chase DataFrame."""
    global chase_df_2
    
    if chase_df_2 is None:
        print("Error: The transaction data has not been preprocessed yet.")
        return None, None
    
    print(f'Mapping transactions with COA file: {file_coa}')
    
    # Read the chart of accounts (COA) file
    try:
        coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
        print(f"COA file loaded successfully: {file_coa}")
    except Exception as e:
        print(f"Error loading COA file {file_coa}: {e}")
        return None, None
    
    # Initialize a variable to track how many rows do not match COA
    mia = 0
    
    # Iterate through each row in the chase DataFrame
    for i, row in chase_df_2.iterrows():
        match = False
        
        if chase_df_2.loc[i, 'Details'] != 'CHECK':  # Skip 'CHECK' related logic
            for j, coa_row in coa.iterrows():
                if coa.loc[j, 'DESCRIPTION'] in chase_df_2.loc[i, 'Description']:
                    match = True
                    chase_df_2.loc[i, 'KEY'] = coa.loc[j, 'EXPENSE']
                    
            # If no match found, increment 'mia'
            if not match:
                mia += 1
                print(i, chase_df_2.loc[i, 'KEY'], chase_df_2.loc[i, 'Description'], chase_df_2.loc[i, 'Amount'])

    print(f'MIA = {mia}')
    
    return mia, chase_df_2


def group_expenses():
    """Group the expenses based on the KEY column."""
    global chase_df_2
    
    # Group the transactions by KEY and sum the amounts
    x = chase_df_2.groupby(['KEY'])[['Amount']]
    y = x.sum()
    
    # Read the Chart of Accounts Key (COA) file
    key = pd.read_csv('Chart_Of_Accounts_Key.txt', encoding='latin1', thousands=',')
    
    # Merge the grouped data with the COA key based on the KEY column
    e = pd.merge(key, y, how='outer', on='KEY')
    
    # Invert the amounts (multiply by -1)
    e['Amount'] = e['Amount'] * -1
    
    # Query the results to filter positive amounts (expenses)
    expense_sum = e.query('Amount > 0')
    
    # Save the result to a CSV file in the same directory as the script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    save_path = os.path.join(script_dir, "Expense.csv")
    
    print("Your tax file is saved to the following location:")
    print(save_path)
    
    # Save the DataFrame to the CSV file
    expense_sum.to_csv(save_path)
    print("File saved successfully.")


def join(file_coa):
    """Map the transactions with the COA and then group the expenses."""
    global chase_df_2
    
    print('join')
    # Ensure the global chase_df_2 is not None (file should be loaded and processed)
    if chase_df_2 is None:
        print("Error: The transaction data has not been loaded yet.")
        return
    
    print(f'Mapping transactions with COA file: {file_coa}')
    
    # Call the map function to map the transactions with the COA
    mia, mapped_transactions = map(file_coa)
    
    if mia:
        print(f"Warning: There are {mia} transactions MIA.")
    
    # Call group_expenses to group the expenses and save the result
    group_expenses()


# Example of running the code
if __name__ == "__main__":

    # COA file name
    file_coa = "Chart_Of_Accounts_Mappings.txt"

    # Provide path to the transaction file here
    # transaction_file_name = "/Users/2021sam/Desktop/2024 Tax/Last year (2024)_2613.CSV"
    transaction_file_name = "/Users/2021sam/Desktop/2024 Tax/Chase0106_Activity_20250205.CSV"
    # Preprocess the transaction file
    chase_df_2 = preprocess_file(transaction_file_name)
    
    if chase_df_2 is not None:
        # If preprocessing is successful, proceed to join and map with COA
        join(file_coa)
    else:
        print("Error: Preprocessing failed. Exiting.")
