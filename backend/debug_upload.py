import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/mudsassir/Desktop/CODING/project_01/backend')

from app.rag.parser import parse_file
from app.rag.chunker import chunk_text
from app.rag.embedder import embed_chunks

path = sys.argv[1] if len(sys.argv) > 1 else '/home/mudsassir/Desktop/CODING/project_01/README.md'

print(f"[1] parsing {path}")
t = time.perf_counter()
pages = parse_file(path)
print(f"    parse_file returned {len(pages)} pages in {time.perf_counter()-t:.2f}s")

print(f"[2] chunking")
t = time.perf_counter()
all_chunks = []
for page in pages:
    chunks = chunk_text(page["text"])
    all_chunks.extend(chunks)
print(f"    chunk_text returned {len(all_chunks)} chunks in {time.perf_counter()-t:.2f}s")

print(f"[3] embedding")
t = time.perf_counter()
texts = [c["text"] for c in all_chunks[:10]]
embeddings = embed_chunks(texts)
print(f"    embed_chunks returned {len(embeddings)} vectors in {time.perf_counter()-t:.2f}s")

print("DONE")
