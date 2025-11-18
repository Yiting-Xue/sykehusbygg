import pandas as pd
from pathlib import Path
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
#from transformers import AutoTokenizer
import tiktoken
import sys

# its different for running these codes directly and running as a python file, so...
try:
    current_file = Path(__file__).resolve()
except NameError:
    current_file = Path(sys.argv[0]).resolve()

for parent in current_file.parents:
    if (parent / "sykehusbygg" / "resource").exists():
        project_root = parent
        break
else:
    raise FileNotFoundError("Fant ikke prosjektrot med 'sykehusbygg/resource'")


klassifikasjon_fi = project_root / "sykehusbygg" / "resource" / "Klassifikasjonssystemet.xlsx"


# Read all sheets from the klassfikasjon file
sheet_names = ["Hovedfunksjon", "Delfunksjon", "Rel_Delfunksjon", "RomNavn", "RomSpesifikasjon"]
dfs = pd.read_excel(klassifikasjon_fi, sheet_name=sheet_names, engine="openpyxl")

for name in sheet_names:
    globals()[f"{name}"] = dfs[name]


merged_df = (
    Hovedfunksjon
    .merge(Delfunksjon, on="HFID", how="left", suffixes=("", "_DF"))
    .merge(Rel_Delfunksjon, on="DFID", how="left", suffixes=("", "_rel_del"))
    .merge(RomSpesifikasjon, on="RSID", how="left", suffixes=("", "_RS"))
    .merge(RomNavn, on="RNID", how="left", suffixes=("", "_RN"))
)

suffix_map = {
    "Hovedfunksjon": "_HF",
    "Delfunksjon": "_DF",
    "Rel_Delfunksjon": "_rel_del",
    "RomSpesifikasjon": "_RS",
    "RomNavn": "_RN"
}

keys = {"HFID", "DFID", "RSID", "RNID"}

# add a suffix to each column except those used as key
for col in merged_df.columns:
    if col in keys:
        continue
    if col in Hovedfunksjon.columns:
        merged_df.rename(columns={col: col + suffix_map["Hovedfunksjon"]}, inplace=True)
    elif col in Delfunksjon.columns:
        merged_df.rename(columns={col: col + suffix_map["Delfunksjon"]}, inplace=True)
    elif col in Rel_Delfunksjon.columns:
        merged_df.rename(columns={col: col + suffix_map["Rel_Delfunksjon"]}, inplace=True)
    elif col in RomSpesifikasjon.columns:
        merged_df.rename(columns={col: col + suffix_map["RomSpesifikasjon"]}, inplace=True)
    elif col in RomNavn.columns:
        merged_df.rename(columns={col: col + suffix_map["RomNavn"]}, inplace=True)


merged_df.shape
#print(merged_df.head())
merged_df.columns

""" # 
tokenizer = AutoTokenizer.from_pretrained("gpt2")

merged_df["token_count"] = merged_df.apply(
    lambda row: len(tokenizer.encode(str(row.to_dict()))),
    axis=1
)
merged_df.drop(columns=["token_count"], inplace=True) """

# for each row in the flattened table, i make a new column which combines each column header and its value and put these pairs in one column and chunking is done on this column. 
# the priciple of chunking is that if a row's combined_text is less than 800 token, i keep it as it is. if over 800 token, chunk but not breaking any column header: column value pair and keep the HFID、DFID、RSID、RNID in each chunk
# I think we need to keep the column name: column value pair. It is not enough just to combine all cell values in a row without telling what these values are for.
merged_df["combined_text"] = merged_df.apply(
    lambda row: "; ".join([f"{col}: {str(row[col])}" for col in merged_df.columns]),
    axis=1
)

#merged_df["token_count"] = merged_df["combined_text"].apply(lambda text: len(encoding.encode(text)))

encoding = tiktoken.encoding_for_model("gpt-4o")


def chunk_by_column_pairs(text, max_tokens=800, overlap=100):
    pairs = text.split("; ")
    chunks = []
    current_chunk = []
    current_tokens = 0
    for pair in pairs:
        pair_tokens = len(encoding.encode(pair))
        if current_tokens + pair_tokens > max_tokens:
            chunks.append(current_chunk)
            if overlap > 0 and current_chunk:
                overlap_tokens = 0
                overlap_chunk = []
                for p in reversed(current_chunk):
                    t = len(encoding.encode(p))
                    if overlap_tokens + t > overlap:
                        break
                    overlap_chunk.insert(0, p)
                    overlap_tokens += t
                current_chunk = overlap_chunk[:]
                current_tokens = overlap_tokens
            else:
                current_chunk = []
                current_tokens = 0
        current_chunk.append(pair)
        current_tokens += pair_tokens
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def format_chunks(df):
    for _, row in df.iterrows():
        ids = [f"HFID: {row.get('HFID','')}", f"DFID: {row.get('DFID','')}", f"RSID: {row.get('RSID','')}", f"RNID: {row.get('RNID','')}"]
        for chunk in chunk_by_column_pairs(row["combined_text"]):
            yield "\n".join(ids + [""] + chunk)

with open("chunks.txt", "w", encoding="utf-8") as f:
    for block in format_chunks(merged_df):
        f.write(block + "\n" + "="*60 + "\n")






