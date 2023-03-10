#   SAX - Sam Personal Tax Assistant
#   Sam Portillo
#   12/15/2019
#   Revised 2023.03.10
#   Version 1.1
# 
from pathlib import Path

import os
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
import pandas as pd         # pip install pandas
import csv

root = Tk()
menubar = Menu( root )
root.config( menu=menubar)


def search_multiple_mappings(file_coa):
    #   Mapping expenses uses first match.
    #      This implies j can be in i but i can not be in j
    # COSTCO
    # COSTCO GAS        # In this case, no write off for gas

    coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
    match = False
    for i, row in coa.iterrows():
        for j, row in coa.iloc[i+1:].iterrows():
            if coa.loc[i, 'DESCRIPTION'] in coa.loc[j, 'DESCRIPTION']:
                match = True
                print(i+2, coa.loc[i, 'DESCRIPTION'], j+2, coa.loc[j, 'DESCRIPTION'] )     # Add 1 for headings + 1 for index to id

    if match:
        print('Fail ! Multiple mappings found.')
    if not match:
        print('Success !  No multiple matches.')


def locate_transaction_file():
    # transaction_file_name = filedialog.askopenfilename()
    csv = 'Chase0106_Activity_20230308.CSV'
    cwd = str(Path.cwd())
    transaction_file_name = Path(Path.cwd(), csv)
    label_transaction_file['text'] = transaction_file_name
    print( transaction_file_name )
    user_path_field.set( os.path.dirname(transaction_file_name) )         # Set path


def get_checks():
    with open('checks.csv', newline='') as csvfile:
        check_mappings = csv.reader(csvfile, delimiter=',', quotechar='|')
        checks = {}
        for row in check_mappings:
            checks[ int(row[0]) ] = int(row[1])
    print(checks)
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
            print( check_number )
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
    checks_sorted = sorted( checks )
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


# Create the submenu
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=subMenu)
subMenu.add_command(label="Exit", command=root.destroy)
subMenu.add_command(label="Goooooo", command= lambda: join(file_coa) )

def about_us():
    tkinter.messagebox.showinfo('About Sam\'s Tax Assistant', 'This indexes the Chart Of Account reference to your expenses.  Developed by Sam Portillo - 510.246.5504')


def help():
    tkinter.messagebox.showinfo('Help', 'Import tax file with header.\rThis header will be skipped with skiprows.')


def test():
    root.destroy()


file_coa = "Chart_Of_Accounts_Mappings.txt"
transaction_file_name = 'Chase0106_Activity_20230308.CSV'

# Main
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=subMenu)
subMenu.add_command(label="About Us", command=about_us)
subMenu.add_command(label="Help Me", command=help)

subMenu = Menu(menubar, tearoff=0)
subMenu.add_cascade(label="Tax", command=join)

root.geometry('500x300')
root.title('2022 Tax Assistant')
button1 = Button( text ="Import Expense File", command=locate_transaction_file ).grid(row=0, column=0, sticky=W)
label_transaction_file = Label( root, text='?')
label_transaction_file.grid(row=0, column=1, sticky=W)

cwd = str(Path.cwd())
f = Path(Path.cwd(), transaction_file_name)
button4 = Button(root, text = "List Checks", command = lambda: list_checks(transaction_file_name)  ).grid(row=5, column=0)
button2 = Button(root, text = "Identity Duplicate Mappings", bg='blue', command = lambda: search_multiple_mappings(file_coa)  ).grid(row=7, column=0)
button3 = Button(root, text = "Identity Transactions MIA", bg='RED', command = lambda: map(file_coa, f) ).grid(row=9, column=0, sticky=W)

Label( root, text='Path').grid(row=3, column=0, sticky=W)
user_path_field = StringVar()
entry_path = Entry(root, textvariable=user_path_field)
user_path_field.set('?')
entry_path.grid(row=3, column=1)

root.mainloop()
# get_checks()
