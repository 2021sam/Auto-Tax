import pandas as pd
file_coa = "Chart_Of_Accounts_Mappings.txt"
coa = pd.read_csv(file_coa, encoding='latin1', thousands=',')
print(coa)
coa_sorted = coa.sort_values(by=['EXPENSE', 'DESCRIPTION'])
print(coa_sorted)
coa_sorted.to_csv('sorted_' + file_coa, index=False)
