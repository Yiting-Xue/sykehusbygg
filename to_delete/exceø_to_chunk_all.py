import pandas as pd
import json
from pathlib import Path

# 手动指定根目录路径
fo = Path("..").resolve()
katalog_fi = fo / "sykehusbygg" / "resource" / "Standardromkatalog v4.0-04.11.2025.xlsx"

# 读取所有 sheet
sheets = pd.read_excel(katalog_fi, sheet_name=None, engine="openpyxl")

# 获取第一个 sheet 的名字和内容
first_sheet_name = list(sheets.keys())[0]
first_sheet_df = sheets[first_sheet_name]

print(f"First sheet name: {first_sheet_name}")
print(first_sheet_df.head())

RFP = first_sheet_df

# 找出所有列名中包含 'Ja/Nei' 的列
ja_nei_columns = [col for col in RFP.columns if 'Ja/Nei' in col]

# 替换这些列中的 True 和 False 为 'Ja' 和 'Nei'
RFP[ja_nei_columns] = RFP[ja_nei_columns].replace({True: 'Ja', False: 'Nei'})

RFP = RFP.fillna("ikke relevant for dette rommet")

def format_row_chunks(df):
    for _, row in df.iterrows():
        base_info = [
            "RFP (hva er det)",
            "Dette er en beskrivelse av noen av funksjonene i et rom",
            f"Kode: {row.get('Kode', '')}",
            f"Navn: {row.get('Navn', '')}",
            f"Standard areal: {row.get('Standard areal', '')}",
            f"Beskrivelse: {row.get('Beskrivelse', '')}",
            ""
        ]

        prefixes = {}
        for col in row.index:
            if ' - ' in col:
                prefix = col.split(' - ')[0]
                prefixes.setdefault(prefix, []).append(col)

        chunks = []
        for prefix, cols in prefixes.items():
            chunk = base_info.copy()
            chunk.append(f"Under følger detaljer for {prefix}:\n")
            for col in cols:
                if pd.notna(row[col]):
                    short_col = col.replace(prefix + ' - ', '')
                    chunk.append(f"{short_col}: {row[col]}")
            chunks.append("\n".join(chunk))

        yield "\n----------------------------------------------\n".join(chunks)

# 示例：打印前3行的格式化结果
for i, formatted in enumerate(format_row_chunks(RFP)):
    if i >= 5:
        break
    print(formatted)
    print("\n============================================================\n")