import os
import pandas as pd
from tkinter import filedialog, Tk

def select_transaction_file():
    """Open a file dialog to allow user to select a transaction file."""
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select Transaction File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    return file_path


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


# def map(df, file_coa):
#     """Perform the mapping of COA to the global DataFrame and log non-mapped transactions."""
#     print('\nMapping transactions with COA file...')

#     if df is None:
#         print("Error: The transaction data has not been preprocessed yet.")
#         return None, None, None  # Return None for all values if df is empty

#     # Read the COA file
#     try:
#         coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
#         print(f"COA file loaded successfully: {file_coa}")
#     except Exception as e:
#         print(f"Error loading COA file {file_coa}: {e}")
#         return None, None, None

#     mia = 0  # Counter for missing transactions
#     non_mapped_transactions = []  # Store non-mapped transactions

#     # Iterate through each row in the DataFrame
#     for i, row in df.iterrows():
#         match = False

#         # Perform the mapping based on the COA description
#         for j, coa_row in coa.iterrows():
#             if pd.notna(coa.loc[j, 'DESCRIPTION']) and coa.loc[j, 'DESCRIPTION'] in str(df.loc[i, 'Description']):
#                 match = True
#                 df.loc[i, 'KEY'] = coa.loc[j, 'EXPENSE']

#         # If no match found, log missing transactions
#         if not match:
#             mia += 1
#             non_mapped_transactions.append(df.loc[i])

#     # Convert non-mapped transactions list into a DataFrame
#     non_mapped_df = pd.DataFrame(non_mapped_transactions)

#     # Print a clear heading for missing transactions
#     if not non_mapped_df.empty:
#         print("\n⚠️ Missing Transactions (MIA) - Update COA Mappings:")
#         print(f"{'Description':<40} {'Amount':<10}")
#         print("-" * 50)
#         for _, row in non_mapped_df.iterrows():
#             print(f"{row['Description']:<40} {row['Amount']:<10.2f}")

#         # Save non-mapped transactions to a file
#         mia_file = os.path.join(os.path.dirname(__file__), "Non_Mapped_Transactions.csv")
#         non_mapped_df.to_csv(mia_file, index=False)
#         print(f"\n📝 Non-mapped transactions saved to: {mia_file}")

#     return mia, df, non_mapped_df  # Return non-mapped transactions as a DataFrame


def map(df, file_coa):
    """Perform the mapping of COA to the global DataFrame and log non-mapped transactions."""
    print('\nMapping transactions with COA file...')

    if df is None:
        print("Error: The transaction data has not been preprocessed yet.")
        return None, None, None

    # Read the COA file
    try:
        coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
        print(f"COA file loaded successfully: {file_coa}")
    except Exception as e:
        print(f"Error loading COA file {file_coa}: {e}")
        return None, None, None

    mia = 0  # Counter for missing transactions
    non_mapped_list = []  # Store non-mapped transactions

    # Iterate through each row in the DataFrame
    for i, row in df.iterrows():
        match = False

        # Perform the mapping based on the COA description
        for j, coa_row in coa.iterrows():
            if pd.notna(coa.loc[j, 'DESCRIPTION']) and coa.loc[j, 'DESCRIPTION'] in str(df.loc[i, 'Description']):
                match = True
                df.at[i, 'KEY'] = coa.loc[j, 'EXPENSE']
                break  # Stop checking after the first match

        # If no match found, add to non-mapped list
        if not match:
            mia += 1
            non_mapped_list.append(df.iloc[i])  # Store the full row

    # Create DataFrames for mapped and non-mapped transactions
    mapped_transactions = df[df['KEY'].notna()].copy()
    non_mapped_transactions = pd.DataFrame(non_mapped_list)

    # Print non-mapped transactions and save to file
    if not non_mapped_transactions.empty:
        print(f"\n⚠️ {len(non_mapped_transactions)} Transactions Missing COA Mapping!")
        non_mapped_file = os.path.join(os.path.dirname(__file__), "Non_Mapped_Transactions.csv")
        non_mapped_transactions.to_csv(non_mapped_file, index=False)
        print(f"📝 Non-mapped transactions saved to: {non_mapped_file}")

    return mia, mapped_transactions, non_mapped_transactions



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







# def validate_transactions(df, mapped_transactions, non_mapped_transactions):
#     """Validate transaction mappings and generate a summary report."""
#     print("\n🔍 Running Validation Checks...")

#     # Compute totals
#     total_transactions = df['Amount'].sum()
#     total_mapped = mapped_transactions['Amount'].sum()

#     # Only include non-mapped transactions that are truly missing (not just unmapped)
#     total_missing = total_transactions - total_mapped

#     total_debits = df['Debit'].sum() if 'Debit' in df.columns else 0
#     total_credits = df['Credit'].sum() if 'Credit' in df.columns else 0
#     total_debits_credits = total_debits - total_credits  # Debits minus Credits
    
#     # Print calculated values before assertion
#     print(f"Total Transactions: {total_transactions:,.2f}")
#     print(f"Total Mapped Transactions: {total_mapped:,.2f}")
#     print(f"Total Missing Transactions: {total_missing:,.2f}")
#     print(f"Total Debits: {total_debits:,.2f}")
#     print(f"Total Credits: {total_credits:,.2f}")
#     print(f"Total Debits & Credits (Debits - Credits): {total_debits_credits:,.2f}")

#     # Debug: Check for missing transactions
#     difference = total_transactions - total_mapped
#     print(f"\n⚠️ Difference Detected: {difference:.2f}")

#     # Assertion Check (Allow a small rounding tolerance)
#     assert abs(difference) < 0.01, "Error: Mapped transactions do not equal total transactions!"

#     # Create summary dictionary
#     summary = {
#         "Total Transactions": total_transactions,
#         "Total Mapped Transactions": total_mapped,
#         "Total Missing Transactions": total_missing,
#         "Total Debits": total_debits,
#         "Total Credits": total_credits,
#         "Total Debits & Credits (Debits - Credits)": total_debits_credits,
#         "Difference": difference
#     }

#     # Save summary to CSV
#     summary_file = os.path.join(os.path.dirname(__file__), "Transaction_Summary.csv")
#     pd.DataFrame(summary.items(), columns=["Metric", "Value"]).to_csv(summary_file, index=False)

#     print(f"\n📊 **Summary saved to:** {summary_file}")

#     return summary


# def validate_transactions(df, mapped_transactions, non_mapped_transactions):
#     """Validate transaction mappings and generate a summary report."""
#     print("\n🔍 Running Validation Checks...")

#     total_transactions = df['Amount'].sum()
#     total_mapped = mapped_transactions['Amount'].sum()
#     total_non_mapped = non_mapped_transactions['Amount'].sum()

#     # Ensure non-mapped transactions are not already counted
#     total_missing = total_transactions - total_mapped
    
#     print(f"\n🔎 Debug: Non-Mapped Transactions Count = {len(non_mapped_transactions)}")
#     print(f"🔎 Debug: Non-Mapped Transactions Total = {total_non_mapped:,.2f}")
#     print(f"🔎 Debug: Total Missing Transactions = {total_missing:,.2f}")

#     # If non-mapped sum is nonzero but missing transactions is zero, something is double-counted
#     assert round(total_missing, 2) == round(total_non_mapped, 2), \
#         f"Error: Non-mapped transactions do not match missing transactions! (Difference: {total_missing - total_non_mapped:.2f})"

#     print(f"\n⚠️ Difference Detected: {total_missing:.2f}")

#     return {
#         "Total Transactions": total_transactions,
#         "Total Mapped Transactions": total_mapped,
#         "Total Non-Mapped Transactions": total_non_mapped,
#         "Total Missing Transactions": total_missing
#     }


# def validate_transactions(df, mapped_transactions, non_mapped_transactions):
#     """Validate transaction mappings and generate a summary report."""
#     print("\n🔍 Running Validation Checks...")

#     total_transactions = df['Amount'].sum()
#     total_mapped = mapped_transactions['Amount'].sum()
#     total_non_mapped = non_mapped_transactions['Amount'].sum()

#     # Ensure non-mapped transactions are not already counted
#     total_missing = total_transactions - total_mapped
    
#     print(f"\n🔎 Debug: Non-Mapped Transactions Count = {len(non_mapped_transactions)}")
#     print(f"🔎 Debug: Non-Mapped Transactions Total = {total_non_mapped:,.2f}")
#     print(f"🔎 Debug: Total Missing Transactions = {total_missing:,.2f}")

#     # If non-mapped sum is nonzero but missing transactions is zero, something is double-counted
#     assert round(total_missing, 2) == round(total_non_mapped, 2), \
#         f"Error: Non-mapped transactions do not match missing transactions! (Difference: {total_missing - total_non_mapped:.2f})"

#     print(f"\n⚠️ Difference Detected: {total_missing:.2f}")

#     return {
#         "Total Transactions": total_transactions,
#         "Total Mapped Transactions": total_mapped,
#         "Total Non-Mapped Transactions": total_non_mapped,
#         "Total Missing Transactions": total_missing
#     }



# def validate_transactions(df, mapped_transactions, non_mapped_transactions):
#     """Validate transaction mappings and generate a summary report."""
#     print("\n🔍 Running Validation Checks...")

#     total_transactions = df['Amount'].sum()
#     total_mapped = mapped_transactions['Amount'].sum() if not mapped_transactions.empty else 0
#     total_non_mapped = non_mapped_transactions['Amount'].sum() if not non_mapped_transactions.empty else 0

#     # Total missing should match non-mapped transactions
#     total_missing = total_transactions - total_mapped

#     # Debug: Print full breakdown
#     print(f"\n🔎 Debug: Total Transactions = {total_transactions:,.2f}")
#     print(f"🔎 Debug: Total Mapped Transactions = {total_mapped:,.2f}")  # ✅ FIXED: Now printing mapped total
#     print(f"🔎 Debug: Non-Mapped Transactions Count = {len(non_mapped_transactions)}")
#     print(f"🔎 Debug: Non-Mapped Transactions Total = {total_non_mapped:,.2f}")
#     print(f"🔎 Debug: Total Missing Transactions = {total_missing:,.2f}")

#     assert round(total_missing, 2) == round(total_non_mapped, 2), \
#         f"Error: Non-mapped transactions do not match missing transactions! (Difference: {total_missing - total_non_mapped:.2f})"

#     if total_missing > 0:
#         print(f"\n✅ Validation Passed! {total_missing:.2f} in non-mapped transactions need COA assignment.")
#     else:
#         print("\n✅ All transactions are mapped correctly!")

#     return {
#         "Total Transactions": total_transactions,
#         "Total Mapped Transactions": total_mapped,
#         "Total Non-Mapped Transactions": total_non_mapped,
#         "Total Missing Transactions": total_missing
#     }



def validate_transactions(df, mapped_transactions, non_mapped_transactions):
    """Validate transaction mappings and generate a summary report in a clear, math-style format."""
    print("\n🔍 Running Validation Checks...\n")

    total_transactions = df['Amount'].sum()
    total_mapped = mapped_transactions['Amount'].sum() if not mapped_transactions.empty else 0
    total_non_mapped = non_mapped_transactions['Amount'].sum() if not non_mapped_transactions.empty else 0

    # Total missing should match non-mapped transactions
    total_missing = total_transactions - total_mapped
    expected_total = total_mapped + total_non_mapped

    # Prepare summary as a formatted string
    summary_output = f"""
📊 **Transaction Breakdown:**

   🏦 Total Transactions:     {total_transactions:,.2f}
   ✅ Mapped Transactions:    {total_mapped:,.2f}
   ❓ Non-Mapped Transactions: {total_non_mapped:,.2f}
   ----------------------------
   🔎 Expected Total:         {expected_total:,.2f}
"""

    # Validation check
    if round(total_transactions, 2) == round(expected_total, 2):
        summary_output += "\n✅✅✅ Everything balances! Your transactions are fully accounted for! ✅✅✅\n"
    else:
        summary_output += f"\n❌ ERROR: Expected Total ({expected_total:,.2f}) does not match Total Transactions ({total_transactions:,.2f})!\n"

    # Print to console
    print(summary_output)

    # Save summary to a text file
    summary_file = os.path.join(os.path.dirname(__file__), "Transaction_Summary.txt")
    with open(summary_file, "w") as file:
        file.write(summary_output)

    print(f"📄 **Summary saved to:** {summary_file}")

    return {
        "Total Transactions": total_transactions,
        "Total Mapped Transactions": total_mapped,
        "Total Non-Mapped Transactions": total_non_mapped,
        "Expected Total": expected_total
    }


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
    # Provide path to the transaction file here
    # transaction_file_name = os.path.join(os.path.dirname(__file__), 'data', 'transactions', 'Chase0106_Activity_20250205.CSV')
    # Ask user to select the transaction file
    transaction_file_name = select_transaction_file()

    if not transaction_file_name:
        print("No file selected. Exiting...")
        exit()

    df = import_data(transaction_file_name)

    # Relative path to the COA file
    file_coa = os.path.join(os.path.dirname(__file__), 'data', 'coa', 'Chart_Of_Accounts_Mappings.txt')


    # Check if both 'Debit' and 'Credit' columns are present
    if 'Debit' in df.columns and 'Credit' in df.columns:
        df = preprocess_file(df)
        print('**************************  PRE PROCESSING IS COMPLETE')

    df['KEY'] = None  # Add a new column called 'KEY' with a default value
    
    # # Call the map function to map the transactions with the COA
    # mia, mapped_transactions = map(df, file_coa)
    # print(f"Warning: There are {mia} transactions MIA.")

    # # Get non-mapped transactions
    # non_mapped_transactions = df[df['KEY'].isna()]

    # # Validate transactions and generate summary
    # validate_transactions(df, mapped_transactions, non_mapped_transactions)

    # expense_sum = group_expenses(mapped_transactions)
    # save_expenses_to_csv(expense_sum)


    # Call the map function to map the transactions with the COA and get non-mapped transactions
    mia, mapped_transactions, non_mapped_transactions = map(df, file_coa)

    print(f"\n🔎 Debug: Non-Mapped Transactions Count = {len(non_mapped_transactions)}")
    print(f"🔎 Debug: Non-Mapped Transactions Total = {non_mapped_transactions['Amount'].sum():,.2f}")


    # Validate transactions and generate summary
    validate_transactions(df, mapped_transactions, non_mapped_transactions)

    expense_sum = group_expenses(mapped_transactions)
    save_expenses_to_csv(expense_sum)
