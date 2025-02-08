column_mapping = {
    "Date": "Posting Date",       # Map Date to Posting Date
    "Description": "Description", # Direct mapping
    "Debit": "Amount",            # Debit becomes Amount
    "Credit": "Amount",           # Credit becomes Amount (negative)
}

# print( column_mapping.items() )
print(column_mapping['Date'])
