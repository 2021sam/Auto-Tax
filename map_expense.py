"""
================================================================================
 Transaction Mapping & Expense Categorization Script
================================================================================
 Author:       Sammy Portillo  
 Created:      01/01/2016
 Description:  This script processes financial transactions, maps them to a
               Chart of Accounts (COA), and generates categorized reports.
               
 Features:
 ✅ Reads transaction data from CSV.
 ✅ Maps transactions based on COA descriptions.
 ✅ Assigns account names using a COA Key file.
 ✅ Saves mapped and non-mapped transactions separately.
 ✅ Generates professional HTML previews for review.
 ✅ Groups transactions by expense categories.
 ✅ Provides detailed logging with checkmarks for easy debugging.

 File Outputs:
 - Mapped_Transactions.csv      → Contains successfully mapped transactions.
 - Non_Mapped_Transactions.csv  → Contains transactions that need COA updates.
 - Mapped_Transactions_Preview.html → HTML table preview of mapped transactions.
 - Non_Mapped_Transactions_Preview.html → HTML table preview of non-mapped transactions.
 - Expense.csv                  → Summary of grouped expenses.

 Dependencies:
 - pandas
 - tabulate (for console table formatting)

 Notes:
 - Transactions with KEY = 0 are classified as "Non Expense."
 - The COA Key file must contain a mapping for all expected expense categories.

================================================================================
"""


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


def initialize_transaction_columns(df):
    """Ensure required columns exist in the DataFrame before processing."""
    required_columns = ['KEY']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""  # Ensure the column exists

    print(f"✅ Initialized columns: {df.columns.tolist()}")
    return df

def load_coa(file_coa):
    """Load the COA mapping file with error handling."""
    try:
        coa_df = pd.read_csv(file_coa, encoding='latin1', thousands=',')
        print(f"✅ COA file loaded successfully: {file_coa}")
        print(f"📊 COA Columns: {coa_df.columns.tolist()}")
        return coa_df
    except Exception as e:
        print(f"❌ Error loading COA file {file_coa}: {e}")
        return None

def load_coa_key(file_coa_key):
    """Load the Chart of Accounts Key file to retrieve account names."""
    try:
        coa_key_df = pd.read_csv(file_coa_key, encoding='latin1', thousands=',')
        print(f"✅ COA Key file loaded successfully: {file_coa_key}")
        print(f"📊 COA Key Columns: {coa_key_df.columns.tolist()}")
        return coa_key_df
    except Exception as e:
        print(f"❌ Error loading COA Key file {file_coa_key}: {e}")
        return None

def map_single_transaction(transaction, coa_df):
    """Map a single transaction to COA based on the description."""
    for _, coa_row in coa_df.iterrows():
        if pd.notna(coa_row['DESCRIPTION']) and coa_row['DESCRIPTION'] in str(transaction['Description']):
            return {'KEY': coa_row['EXPENSE']}

    return {'KEY': None}  # If no match is found


def map_transactions(df, coa_df):
    """Map all transactions in the DataFrame using the COA file."""
    mapped_list = []
    non_mapped_list = []
    
    for _, transaction in df.iterrows():
        mapped_data = map_single_transaction(transaction, coa_df)

        if mapped_data['KEY'] is None:
            # ✅ Convert transaction to dictionary and remove 'KEY'
            transaction_dict = transaction.to_dict()
            transaction_dict.pop('KEY', None)  # Remove 'KEY' immediately
            non_mapped_list.append(transaction_dict)
        else:
            transaction['KEY'] = mapped_data['KEY']
            mapped_list.append(transaction.to_dict())

    # ✅ Create DataFrames after 'KEY' is already removed
    mapped_df = pd.DataFrame(mapped_list)
    non_mapped_df = pd.DataFrame(non_mapped_list)

    print(f"✅ {len(mapped_df)} Transactions Mapped Successfully!")
    print(f"⚠️ {len(non_mapped_df)} Transactions Missing COA Mapping!")

    return mapped_df, non_mapped_df



def assign_account_names(df, coa_key_df):
    """Assign proper account names to transactions using the Chart of Accounts Key file."""
    if coa_key_df is None or df.empty:
        print("❌ Skipping account name assignment due to missing data.")
        return df

    # Convert 'KEY' to string before merging
    df['KEY'] = df['KEY'].astype(str)
    coa_key_df['KEY'] = coa_key_df['KEY'].astype(str)

    df = df.merge(coa_key_df[['KEY', 'ACCOUNT']], on='KEY', how='left')
    df['ACCOUNT'].fillna("UNKNOWN ACCOUNT", inplace=True)  # ✅ Default for unmapped transactions

    print(f"✅ Assigned account names using COA Key file.")
    return df

def save_to_csv(df, filename, message):
    """Save any DataFrame to CSV with error handling and logging."""
    if not df.empty:
        file_path = os.path.join(os.path.dirname(__file__), filename)
        df.to_csv(file_path, index=False)
        print(f"📄 {message}: {file_path}")

def process_transaction_mapping(df, file_coa, file_coa_key):
    """Wrapper function to handle the full transaction mapping process."""
    df = initialize_transaction_columns(df)
    coa_df = load_coa(file_coa)
    coa_key_df = load_coa_key(file_coa_key)

    if coa_df is None:
        print("❌ COA file could not be loaded. Exiting mapping process.")
        return None, None

    mapped_transactions, non_mapped_transactions = map_transactions(df, coa_df)

    # Assign account names using COA Key file
    mapped_transactions = assign_account_names(mapped_transactions, coa_key_df)

    save_to_csv(mapped_transactions, "Mapped_Transactions.csv", "Mapped transactions saved")
    save_to_csv(non_mapped_transactions, "Non_Mapped_Transactions.csv", "Non-mapped transactions saved")

    return mapped_transactions, non_mapped_transactions

def group_expenses(df):
    """Group the expenses based on the KEY column."""
    print("\n🔄 Grouping Expenses by KEY...")

    # Group the transactions by KEY and sum the amounts
    grouped = df.groupby(['KEY'])[['Amount']].sum().reset_index()

    # Load the Chart of Accounts Key file
    key_file = os.path.join(os.path.dirname(__file__), 'data', 'coa', 'Chart_Of_Accounts_Key.txt')
    key = pd.read_csv(key_file, encoding='latin1', thousands=',')

    print(f"✅ COA Key file loaded successfully: {key_file}")

    # 🔹 Ensure 'KEY' is the same type in both DataFrames
    grouped['KEY'] = grouped['KEY'].astype(str)
    key['KEY'] = key['KEY'].astype(str)

    # Merge the grouped data with the COA key based on the KEY column
    merged_expenses = pd.merge(key, grouped, how='outer', on='KEY')

    print("✅ Successfully grouped and merged expenses!\n")

    return merged_expenses

def save_expenses_to_csv(expense_sum):
    """Save the expenses DataFrame to a CSV file."""
    save_path = os.path.join(os.path.dirname(__file__), "Expense.csv")
    
    print("📄 Your tax file is saved to the following location:")
    print(save_path)
    
    # Save the DataFrame to the CSV file
    expense_sum.to_csv(save_path, index=False)
    print("✅ File saved successfully.")





import pandas as pd
from tabulate import tabulate

def save_to_preview(df, filename):
    """Save DataFrame to CSV and display a preview table."""
    
    # Step 1: Save the DataFrame to CSV
    df.to_csv(filename, index=False)
    print(f"✅ {filename} saved successfully.")

    # Step 2: Display a preview table (first 5 rows)
    print("\n📊 Preview Table (First 5 rows):")
    print(tabulate(df.head(), headers='keys', tablefmt='pretty'))

# # Example usage:
# mapped_transactions = pd.read_csv('Mapped_Transactions.csv')
# save_to_preview(mapped_transactions, 'Mapped_Transactions_Updated.csv')


import pandas as pd

def save_to_html_preview(df, filename):
    """Save DataFrame to HTML and display a preview with styling."""
    
    # Step 1: Save the DataFrame to an HTML file with styling
    html_table = df.to_html(index=False, classes="table table-striped table-bordered", border=0)
    
    # Add some basic styling to the table
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .table th, .table td {{
                padding: 8px 12px;
                text-align: left;
            }}
            .table th {{
                background-color: #f2f2f2;
                color: #333;
            }}
            .table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .table-bordered {{
                border: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <h2>Mapped Transactions (Preview)</h2>
        {html_table}
    </body>
    </html>
    """
    
    # Step 2: Write the HTML content to a file
    with open(filename, "w") as file:
        file.write(html_content)

    print(f"✅ HTML file saved successfully as {filename}.")

# # Example usage:
# mapped_transactions = pd.read_csv('Mapped_Transactions.csv')
# save_to_html_preview(mapped_transactions, 'Mapped_Transactions_Preview.html')



if __name__ == "__main__":
    # transaction_file_name = "transactions.csv"  # Replace with `select_transaction_file()` if needed
    transaction_file_name = select_transaction_file()
    
    if not transaction_file_name:
        print("❌ No file selected. Exiting...")
        exit()

    file_coa = os.path.join(os.path.dirname(__file__), 'data', 'coa', 'Chart_Of_Accounts_Mappings.txt')
    file_coa_key = os.path.join(os.path.dirname(__file__), 'data', 'coa', 'Chart_Of_Accounts_Key.txt')

    df = pd.read_csv(transaction_file_name)

    if 'Debit' in df.columns and 'Credit' in df.columns:
        df['Amount'] = df['Debit'].fillna(0) - df['Credit'].fillna(0)  # Convert Debits/Credits to Amount
        print('✅ Preprocessing Complete!')

    mapped_transactions, non_mapped_transactions = process_transaction_mapping(df, file_coa, file_coa_key)

    expense_sum = group_expenses(mapped_transactions)
    save_expenses_to_csv(expense_sum)
    save_to_preview(mapped_transactions, 'Mapped_Transactions_Updated.csv')
    save_to_html_preview(non_mapped_transactions, "Non_Mapped_Transactions_Preview.html")
    save_to_html_preview(mapped_transactions, 'Mapped_Transactions_Preview.html')


    print("✅✅✅ Processing Complete! All files are saved. 🚀")
