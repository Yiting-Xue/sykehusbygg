import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# --- Load JSON ---
json_path = Path("C:/Users/YitingXue/sykehusbygg/data/standardromkatalogen.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rooms = data.get("RFP", [])

# --- Token counter ---
enc = tiktoken.encoding_for_model("gpt-4o")
def count_tokens(text: str) -> int:
    return len(enc.encode(text))

# --- Format room ---
def format_room(entry: dict) -> str:
    parts = []
    for key, value in entry.items():
        if value:
            parts.append(f"{key}: {value}")
    return "\n".join(parts)

# --- Chunking test ---
def test_chunking(chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []

    for room in rooms:
        text = format_room(room)
        if count_tokens(text) <= 500:
            chunks.append(text)
        else:
            chunks.extend(splitter.split_text(text))

    token_counts = [count_tokens(c) for c in chunks]
    avg_tokens = sum(token_counts) / len(token_counts)

    print(f"\n=== chunk_size={chunk_size}, overlap={chunk_overlap} ===")
    print(f"Total chunks: {len(chunks)}")
    print(f"Average tokens per chunk: {avg_tokens:.2f}")
    print(f"Sample chunk:\n{chunks[0]}")
    print(f"Token count: {token_counts[0]}")

# --- Run tests ---
test_chunking(1000, 200)
test_chunking(1500, 300)
test_chunking(500, 100)
