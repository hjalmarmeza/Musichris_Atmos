import pandas as pd

try:
    xlsx = pd.ExcelFile('/Users/hjalmarmeza/Downloads/Antigravity/Musichris_Atmos/data/spreadsheet_full.xlsx')
    print(f"Sheets found: {xlsx.sheet_names}")
    for sheet_name in xlsx.sheet_names:
        df = xlsx.parse(sheet_name)
        print(f"Sheet '{sheet_name}': {len(df)} rows")
        if 'Título' in df.columns or 'B' in df.columns:
            print(f"  Sample Título: {df.iloc[-1]['Título'] if 'Título' in df.columns else 'N/A'}")
except Exception as e:
    print(f"Error: {e}")
