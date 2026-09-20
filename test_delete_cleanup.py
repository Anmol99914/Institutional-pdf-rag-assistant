"""
Delete-cleanup test. Run from the project root:

    python test_delete_cleanup.py

It works in a temporary sandbox (fake PDFs, real Markdown helpers, real VectorStore),
so your real data/, vector_store/ and index files are never modified.
Run it against the OLD app.py to see the bug, then against the fixed one.
"""
import os
import shutil
import sys
import tempfile
from urllib.parse import quote

import faiss
import numpy as np

import app as appmod
from src.indexer import load_existing_index
from src.md_converter import markdown_already_exists, pdf_pages_to_markdown
from src.vector_store import VectorStore

DIM = 8
TARGET = "Unit 2 - Perspectives in management.pdf"   # spaces, as stored in your index
OTHER = "Anmols_CV.pdf"

failures = 0


def check(label, condition):
    global failures
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        failures += 1


def unit(i):
    v = np.zeros(DIM, dtype="float32")
    v[i] = 1.0
    return v


# ---------------------------------------------------------------- sandbox
tmp = tempfile.mkdtemp(prefix="rag_delete_test_")
uploads = os.path.join(tmp, "data", "uploads")
md_dir = os.path.join(tmp, "data", "markdown")
vs_dir = os.path.join(tmp, "vector_store")
for d in (uploads, md_dir, vs_dir):
    os.makedirs(d)

index_path = os.path.join(vs_dir, "faiss.index")
metadata_path = os.path.join(vs_dir, "metadata.pkl")

# Point the app at the sandbox (routes read these module-level names at call time)
appmod.UPLOAD_DIR = uploads
appmod.MARKDOWN_DIR = md_dir
appmod.INDEX_PATH = index_path
appmod.METADATA_PATH = metadata_path

store = VectorStore(dim=DIM)
# TARGET is added first, so deleting it shifts OTHER's vector positions.
# That lets the test prove vectors and metadata stay aligned afterwards.
layout = {TARGET: (0, 1), OTHER: (2, 3)}
for name, (a, b) in layout.items():
    with open(os.path.join(uploads, name), "wb") as f:
        f.write(b"%PDF-1.4\n")
    pdf_pages_to_markdown([{"text": f"text of {name}", "source": name, "page": 1}], name, md_dir)
    chunks = [{"source": name, "page": 1, "text": f"{name} p1"},
              {"source": name, "page": 2, "text": f"{name} p2"}]
    store.add(np.stack([unit(a), unit(b)]), chunks)
store.save(index_path, metadata_path)

appmod.vector_store = store
appmod.processed_files = sorted(layout)
appmod.processed_file_count = len(layout)

client = appmod.app.test_client()

# ---------------------------------------------------------------- before
print("\n--- Before deleting ---")
html = client.get("/").get_data(as_text=True)
check("1. both documents are in the processed list", TARGET in html and OTHER in html)
check("   both PDFs exist", all(os.path.isfile(os.path.join(uploads, n)) for n in layout))
check("   both Markdown files exist", all(markdown_already_exists(n, md_dir)[0] for n in layout))
check("   FAISS index holds 4 vectors", faiss.read_index(index_path).ntotal == 4)

# ---------------------------------------------------------------- delete
print("\n--- Deleting through the app ---")
resp = client.post("/delete/" + quote(TARGET))
data = resp.get_json()
check(f"2. delete request succeeded (HTTP {resp.status_code}, {data})",
      resp.status_code == 200 and data and data.get("success") is True)
check("   response reports 1 remaining document", bool(data) and data.get("processed_file_count") == 1)

check("3. PDF removed from data/uploads", not os.path.exists(os.path.join(uploads, TARGET)))
check("4. Markdown removed from data/markdown", not markdown_already_exists(TARGET, md_dir)[0])

reloaded = load_existing_index(index_path, metadata_path)
check("5. source gone from metadata.pkl (read back from disk)",
      reloaded is not None and TARGET not in {m["source"] for m in reloaded.metadata})
check("6. vectors gone from the saved FAISS index (4 -> 2)",
      faiss.read_index(index_path).ntotal == 2 and len(reloaded.metadata) == 2)

# ---------------------------------------------------------------- refresh / restart
print("\n--- Refresh and restart ---")
html = client.get("/").get_data(as_text=True)
check("7. refreshing / does not bring the document back", TARGET not in html and OTHER in html)
restart_list = sorted(set(c["source"] for c in reloaded.metadata))
check("   a fresh app start would list only the remaining document", restart_list == [OTHER])

# ---------------------------------------------------------------- others intact
print("\n--- Other documents ---")
check("8. other PDF still present", os.path.isfile(os.path.join(uploads, OTHER)))
check("   other Markdown still present", markdown_already_exists(OTHER, md_dir)[0])
hit1 = reloaded.search(unit(2), top_k=5)
hit2 = reloaded.search(unit(3), top_k=5)
check("   search still works and vectors are aligned with metadata",
      hit1 and hit1[0][0]["source"] == OTHER and hit1[0][0]["page"] == 1 and hit1[0][1] > 0.99
      and hit2 and hit2[0][0]["source"] == OTHER and hit2[0][0]["page"] == 2)
check("   no deleted-document chunks are retrievable",
      all(c["source"] == OTHER for c, _ in reloaded.search(unit(0), top_k=5)))

# ---------------------------------------------------------------- edge cases
print("\n--- Edge cases ---")
resp = client.post("/delete/" + quote("Does not exist.pdf"))
data = resp.get_json()
check("unknown document -> success False, HTTP 404",
      resp.status_code == 404 and data and data.get("success") is False)
resp = client.post("/delete/" + quote("sub/evil.pdf"))
check("path-like name is rejected (400/404) and nothing else is deleted",
      resp.status_code in (400, 404) and os.path.isfile(os.path.join(uploads, OTHER)))
check("other document still indexed after the edge cases",
      sorted(set(c["source"] for c in appmod.vector_store.metadata)) == [OTHER])

shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL CHECKS PASSED" if failures == 0 else f"{failures} CHECK(S) FAILED"))
sys.exit(1 if failures else 0)