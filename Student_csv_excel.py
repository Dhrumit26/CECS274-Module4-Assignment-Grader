# install dependencies first:
# pip install pandas openpyxl

import pandas as pd

# Step 1: specify input CSV and output Excel filenames
csv_file = "m4_code_summary.csv"       # <-- change this to your CSV file path
excel_file = "Student_grades.xlsx"   # <-- desired Excel output file

# Step 2: read the CSV file
df = pd.read_csv(csv_file)

# Step 3: write to Excel
df.to_excel(excel_file, index=False)

print(f"✅ Successfully converted '{csv_file}' → '{excel_file}'")
