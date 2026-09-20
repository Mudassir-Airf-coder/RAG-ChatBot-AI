import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/mudsassir/Desktop/CODING/project_01/backend')

from app.rag.parser import parse_file
from app.rag.chunker import chunk_text

path = sys.argv[1] if len(sys.argv) > 1 else '/home/mudsassir/Desktop/CODING/project_01/README.md'

print(f"[1] parsing {path}")
pages = parse_file(path)
print(f"    parsed {len(pages)} pages")

for i, page in enumerate(pages):
    text = page["text"]
    print(f"[2.{i}] chunking page {i} ({len(text)} chars)")
    t = time.perf_counter()
    chunks = chunk_text(text)
    print(f"      -> {len(chunks)} chunks in {time.perf_counter()-t:.3f}s")

print("DONE")
