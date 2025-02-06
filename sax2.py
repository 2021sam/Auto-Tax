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



def search_multiple_mappings(file_coa):
    coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
    match = False
    for i, row in coa.iterrows():
        for j, row in coa.iloc[i+1:].iterrows():
            if coa.loc[i, 'DESCRIPTION'] in coa.loc[j, 'DESCRIPTION']:
                match = True
                print(i+2, coa.loc[i, 'DESCRIPTION'], j+2, coa.loc[j, 'DESCRIPTION'] )     # Add 1 for headings + 1 for index to id
    if match:
        print('Fail ! Multiple mappings found.')
        tkinter.messagebox.showinfo('Fail !', 'Fail ! Multiple mappings found.')

    if not match:
        print('Success !  No multiple matches.')
        tkinter.messagebox.showinfo(title='Success !', message='No multiple matches.')


# def locate_transaction_file():
#     # transaction_file_name = filedialog.askopenfilename()
#     csv = 'Chase0106_Activity_20230308.CSV'
#     cwd = str(Path.cwd())
#     transaction_file_name = Path(Path.cwd(), csv)
#     label_transaction_file['text'] = transaction_file_name
#     print( transaction_file_name )
#     user_path_field.set( os.path.dirname(transaction_file_name) )         # Set path



def locate_transaction_file():
    # Open file dialog to select a file
    transaction_file_name = filedialog.askopenfilename(title="Select Transaction File", filetypes=[("CSV Files", "*.csv")])

    if transaction_file_name:  # If a file is selected
        try:
            # Read the CSV to check for 'Debit' and 'Credit' columns
            df = pd.read_csv(transaction_file_name, encoding='latin1', thousands=',')
            
            # Check if both 'Debit' and 'Credit' columns are present
            if 'Debit' in df.columns and 'Credit' in df.columns:
                # If the file matches the new format, preprocess it
                preprocess_new_format(df)
                label_transaction_file['text'] = transaction_file_name
                user_path_field.set(os.path.dirname(transaction_file_name))  # Set the path
                print(f"File successfully loaded: {transaction_file_name}")
            else:
                tkinter.messagebox.showerror("Invalid Format", "This file does not match the expected new format.")
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"An error occurred while reading the file: {str(e)}")
    else:
        print("No file selected.")
        

def preprocess_new_format(df):
    """
    Process the CSV file in the new format (separate Debit and Credit columns).
    Converts Credit values into negative Amounts and processes the data.
    """
    # Rename the Debit column to Amount
    df.rename(columns={'Debit': 'Amount'}, inplace=True)

    # Update the Amount column by subtracting Credit (convert Credit to negative values in Amount)
    df['Amount'] = df['Amount'].fillna(0) - df['Credit'].fillna(0)

    # Remove the Credit column as it's no longer needed
    df = df.drop(columns=['Credit'])

    # Show the first few rows to verify
    print(df.head())

    # You can save or continue processing with the Amount column
    # For example, you might want to save it to a new file, apply tax calculations, etc.



def get_checks():
    with open('checks.csv', newline='') as csvfile:
        check_mappings = csv.reader(csvfile, delimiter=',', quotechar='|')
        checks = {}
        for row in check_mappings:
            checks[ int(row[0]) ] = int(row[1])
    return checks


def map(file_coa, transaction_file_name):
    chase = pd.read_csv( transaction_file_name, dtype={7: object}, skiprows = 1 )
    chase.columns.values
    cnames = ["Details","Posting Date","Description","Amount","Type","Balance","Check","KEY"]
    chase.columns = cnames
    chase['KEY'] = chase['KEY'].fillna(0)
    coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
    checks = get_checks()
    mia = 0
    for i, row in chase.iterrows():
        match = False
        if chase.loc[i, 'Details'] == 'CHECK':
            check_number = int(chase.loc[i, 'Check'])
            chase.loc[i, 'KEY'] = checks[check_number]
            # continue
        if chase.loc[i, 'Details'] != 'CHECK':
            for j, row in coa.iterrows():
                if coa.loc[j, 'DESCRIPTION'] in chase.loc[i, 'Description']:
                    match = True
                    chase.loc[i, 'KEY'] = coa.loc[j, 'EXPENSE']
                    # print( i, chase.loc[i, 'KEY'], chase.loc[i, 'Description'], chase.loc[i, 'Amount'] )
            if not match:
                mia += 1
                print( i, chase.loc[i, 'KEY'], chase.loc[i, 'Description'], chase.loc[i, 'Amount'] )
    print(f'MIA = {mia}')
    return mia, chase


def list_checks(transaction_file_name):
    print('list_checks ')
    chase = pd.read_csv( transaction_file_name, dtype={7: object}, skiprows = 1 )
    chase.columns.values
    cnames = ["Details","Posting Date","Description","Amount","Type","Balance","Check","KEY"]
    chase.columns = cnames
    chase['KEY'] = chase['KEY'].fillna(0)
    checks = []
    for i, row in chase.iterrows():
        if chase.loc[i, 'Details'] == 'CHECK':
            v = list( chase.iloc[i] )
            checks.append(int( v[6] ))
    checks_sorted = sorted(checks)
    for i in checks_sorted:
        print(i)


def group_expenses(mapped_transactions):
    x = mapped_transactions.groupby(['KEY'])[['Amount']]
    y = x.sum()
    key = pd.read_csv( 'Chart_Of_Accounts_Key.txt', encoding='latin1', thousands=',')
    e = pd.merge( key, y, how = 'outer', on = 'KEY')
    e['Amount'] = e['Amount'] * -1
    column_names = ["KEY", "ACCOUNT", "Amount"]
    expense_sum = e.query('Amount > 0')
    # print( expense_sum )
    name = os.path.join(user_path_field.get(), "Expense.csv")
    print ( "Your tax file is saved to the following location:")
    #expense_sum.reset_index()
    print ( name )
    expense_sum.to_csv(name)
    root.destroy()


def join(file_coa):
    transaction_file_name = label_transaction_file['text']
    print(f'[{transaction_file_name}]')
    mia, mapped_transactions = map(file_coa, transaction_file_name)
    if mia:
        tkinter.messagebox.showinfo('Warning', f'There are {mia} transactions MIA.')
    group_expenses(mapped_transactions)


def about_us():
    tkinter.messagebox.showinfo('About Sam\'s Tax Assistant', 'This indexes the Chart Of Account reference to your expenses.  Developed by Sam Portillo - 510.246.5504')


def help():
    global label_help
    global button_close_help

    help_height = 500
    root.geometry(f'{app_width}x{help_height}')
    label_help = Label(root, text='', relief=RAISED, justify=LEFT)          # Need to lines to make global, yes weird ?
    # label_help.grid(row = 6, column=0, sticky=W )

    label_help['text'] = 'HELP INFORMATION\n\n' \
    'Import tax file with header.\n' \
    'Details,Posting Date,Description,Amount,Type,Balance,Check or Slip #\n' \
    'This header will be skipped with skiprows.\n' \
    '1. Verify that there are no multiple mappings:\n' \
    '     Mapping expenses uses first match.\n' \
    '     This implies j can be in i but i can not be in j\n' \
    '     i COSTCO\n' \
    '     j COSTCO GAS\n' \
    '     In this case, no write off for fuel expense.\n' \
    '2. Verify that there are no mappings MIA.\n' \
    '3. List unmapped Checks.\n' \
    '   Copy check numbers\n' \
    '   Paste in a new file named checks.csv\n' \
    '   Map to COA Key using the following format\n' \
    '   check number, COA Key\n' \
    '   Click Tax\n' \
    '   Results are in Expense.csv'
    label_help.grid(row = 10, column=0, sticky=W )
    button_close_help = Button( text ="Close Help", command= close_help)
    button_close_help.grid(row=20, column=0, sticky=W)


def close_help():
    global label_help
    global button_close_help
    label_help['text'] = 'Your welcome'
    root.geometry(f'{app_width}x{app_height}')
    button_close_help.destroy()


def test():
    root.destroy()


file_coa = "Chart_Of_Accounts_Mappings.txt"
transaction_file_name = 'Chase0106_Activity_20230308.CSV'


# Menu Bar
exit_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Exit", menu=exit_menu)
exit_menu.add_command(label="Exit", command=root.destroy)

validate_menu = Menu(menu)
menu.add_cascade(label="Validate", menu=validate_menu)
validate_menu.add_command(label="Identify Duplicate Mappings", command = lambda: search_multiple_mappings(file_coa))
validate_menu.add_command(label="Identify Transactions MIA", command = lambda: map(file_coa, f) )

tax_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Tax", menu=tax_menu)
tax_menu.add_command(label="Auto Tax", command= lambda: join(file_coa) )

help_menu = Menu(menu, tearoff=0)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About Us", command=about_us)
help_menu.add_command(label="Help Me", command=help)

root.geometry(f'{app_width}x{app_height}')
root.title('2022 Tax Assistant')

row = 0
button1 = Button( text ="Import Expense File", command=locate_transaction_file ).grid(row=row, column=0, sticky=W)
label_transaction_file = Label( root, text='?')
label_transaction_file.grid(row=row, column=1, sticky=W)

cwd = str(Path.cwd())
f = Path(Path.cwd(), transaction_file_name)

row = 1
path1 = Label( root, text='Path', justify=LEFT).grid(row=row, column=0, sticky=W)
user_path_field = StringVar()
entry_path = Entry(root, textvariable=user_path_field)
user_path_field.set('?')
entry_path.grid(row=row, column=1)

row = 2
button2 = Button(root, text = "Identity Duplicate Mappings", bg='blue', command = lambda: search_multiple_mappings(file_coa)  ).grid(row=row, column=0)

row = 3
button3 = Button(root, text = "Identity Transactions MIA", bg='RED', command = lambda: map(file_coa, f) ).grid(row=row, column=0, sticky=W)

row = 4
button4 = Button(root, text = "List Checks", command = lambda: list_checks(transaction_file_name)  ).grid(row=row, column=0)

row = 5
root.mainloop()
