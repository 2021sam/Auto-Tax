#   SAX - Sam Personal Tax Assistant
#   Sam Portillo
#   12/15/2019
#   Revised 2023.03.10
#   Version 1.1

from pathlib import Path

import os
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
import pandas as pd         # pip install pandas
import csv

root = Tk()
menu = Menu( root )
root.config(menu=menu)
label_help = None
button_close_help = None
app_width = 700
app_height = 150



# Global variable for chase DataFrame
chase_df = None

def preprocess_file(transaction_file_name):
    """Load and preprocess the CSV file, then store the result in a global variable."""
    global chase_df
    
    print('Preprocessing file:', transaction_file_name)
    # Read the CSV, skipping the first row
    chase = pd.read_csv(transaction_file_name, skiprows=1)
    print('File loaded successfully')
    
    # Assign column names
    cnames = ["Details", "Posting Date", "Description", "Amount", "Type", "Balance", "Check", "KEY"]
    chase.columns = cnames
    
    # Fill missing 'KEY' values with 0
    chase['KEY'] = chase['KEY'].fillna(0)
    
    # Store the preprocessed DataFrame globally for later use
    chase_df = chase
    
    print("Preprocessing complete.")
    print(chase_df.head)
    return chase_df


def map(file_coa):
    """Perform the mapping of COA to the global chase DataFrame."""
    global chase_df
    
    if chase_df is None:
        print("Error: The transaction data has not been loaded yet.")
        return
    
    # Read the chart of accounts (COA) file
    coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
    
    # Initialize a variable to track how many rows do not match COA
    mia = 0
    
    # Iterate through each row in the chase DataFrame
    for i, row in chase_df.iterrows():
        match = False
        
        if chase_df.loc[i, 'Details'] != 'CHECK':  # Skip 'CHECK' related logic
            for j, coa_row in coa.iterrows():
                if coa.loc[j, 'DESCRIPTION'] in chase_df.loc[i, 'Description']:
                    match = True
                    chase_df.loc[i, 'KEY'] = coa.loc[j, 'EXPENSE']
                    
            # If no match found, increment 'mia'
            if not match:
                mia += 1
                print(i, chase_df.loc[i, 'KEY'], chase_df.loc[i, 'Description'], chase_df.loc[i, 'Amount'])

    print(f'MIA = {mia}')
    
    return mia, chase_df


def locate_transaction_file():
    """Allow the user to select a CSV file for transaction data."""
    global chase_df
    # root = tk.Tk()
    # root.withdraw()  # Hide the root window (we just want the file dialog)
    
    # Open file dialog to select the transaction file
    transaction_file_name = filedialog.askopenfilename(title="Select Transaction File", filetypes=[("CSV Files", "*.csv")])
    
    if transaction_file_name:
        # Preprocess the selected file and store the result globally
        preprocess_file(transaction_file_name)
        print(f"File successfully loaded: {transaction_file_name}")
        
        # You can now use 'chase_df' in any part of your program
        # For example: Perform mapping with a selected COA file
        # coa_file = filedialog.askopenfilename(title="Select COA File", filetypes=[("CSV Files", "*.csv")])
        # if coa_file:
        #     mia, result_df = map(coa_file)
        #     print(f"Mapping finished. {mia} transactions did not match.")

        # else:
        #     print("No COA file selected.")
    else:
        print("No transaction file selected.")




def group_expenses():
    """Group the expenses based on the KEY column."""
    global chase_df
    
    # Group the transactions by KEY and sum the amounts
    x = chase_df.groupby(['KEY'])[['Amount']]
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
    global chase_df
    
    # Ensure the global chase_df is not None (file should be loaded and processed)
    if chase_df is None:
        print("Error: The transaction data has not been loaded yet.")
        return
    
    print(f'Mapping transactions with COA file: {file_coa}')
    
    # Call the map function to map the transactions with the COA
    mia, mapped_transactions = map(file_coa)
    
    if mia:
        print(f"Warning: There are {mia} transactions MIA.")
    
    # Call group_expenses to group the expenses and save the result
    group_expenses()



# Run the file selection and processing
if __name__ == "__main__":

    file_coa = "Chart_Of_Accounts_Mappings.txt"
    root = Tk()
    root.withdraw()  # Hide the root window (we just want the file dialog)

    locate_transaction_file()
    join(file_coa)

    # root.mainloop()