import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# --- 1. Load JSON file ---
json_path = Path("C:/Users/YitingXue/sykehusbygg/data/standardromkatalogen.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rooms = data.get("RFP", [])

# --- 2. Token counter ---
enc = tiktoken.encoding_for_model("gpt-4o")

def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# --- 3. Format each room into readable text ---
def format_room(entry: dict) -> str:
    parts = []
    for key, value in entry.items():
        if value is not None and value != "":
            parts.append(f"{key}: {value}")
    return "\n".join(parts)

# --- 4. Chunking per room ---
splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
all_chunks = []

for i, room in enumerate(rooms):
    room_text = format_room(room)
    token_count = count_tokens(room_text)

    if token_count <= 500:
        all_chunks.append(room_text)
    else:
        chunks = splitter.split_text(room_text)
        all_chunks.extend(chunks)

# --- 5. Print first few chunks ---
for i, chunk in enumerate(all_chunks[:3]):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk)
    print(f"Token count: {count_tokens(chunk)}")
