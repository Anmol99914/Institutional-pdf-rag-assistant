"""
test_markdown_pipeline.py

End-to-end verification of the PDF -> Markdown -> chunk -> embed -> FAISS
pipeline. Run from your project root (E:\\pdf_rag_assistant) with the
dsml312 conda env active:

    python test_markdown_pipeline.py path\\to\\sample.pdf

This does NOT modify your existing pipeline. It calls your real modules
and reports pass/fail per stage so you can tell exactly where a problem
lives if something's wrong.

--- CONFIG: adjust these three lines if your actual function names in
    pdf_processor.py / indexer.py differ from what's assumed here ---
"""

import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pdf_processor import extract_text_from_pdf     # ADJUST if named differently
from src.md_converter import pdf_pages_to_markdown, parse_markdown_pages, markdown_already_exists
from src.chunker import chunk_text

MARKDOWN_DIR = os.path.join("data", "markdown")  # ADJUST if your markdown dir differs

results = []  # (check_name, passed: bool, detail: str)


def check(name, passed, detail=""):
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))


def normalize_ws(s):
    """Collapse leading/trailing whitespace only -- for the whitespace-tolerant compare."""
    return s.strip("\n") if s is not None else s


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_markdown_pipeline.py path/to/sample.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    print(f"\n=== Testing pipeline on: {pdf_path} ===\n")

    # ---------- 1. Extraction ----------
    try:
        pages = extract_text_from_pdf(pdf_path)  # expected: list of page dicts or (page_num, text) -- see note below
        check("1. PyMuPDF extraction runs", True, f"{len(pages)} pages returned")
    except Exception as e:
        check("1. PyMuPDF extraction runs", False, str(e))
        print_summary()
        return

    # Normalize `pages` into a list of (page_num, text) for this test script's own use,
    # regardless of whether extract_text_from_pdf returns tuples or dicts.
    normalized_pages = []
    for i, p in enumerate(pages, start=1):
        if isinstance(p, tuple):
            normalized_pages.append(p)
        elif isinstance(p, dict):
            page_num = p.get("page", i)
            text = p.get("text", "")
            normalized_pages.append((page_num, text))
        else:
            normalized_pages.append((i, str(p)))

    total_chars_extracted = sum(len(t) for _, t in normalized_pages)
    empty_pages = [n for n, t in normalized_pages if not t or not t.strip()]
    check("1a. Non-trivial text extracted", total_chars_extracted > 0,
          f"total_chars={total_chars_extracted}, empty_pages={empty_pages}")

    # ---------- 2. Markdown file produced ----------
    try:
        md_path, stage_meta = pdf_pages_to_markdown(normalized_pages, pdf_path, MARKDOWN_DIR)
        check("2. .md file written", os.path.exists(md_path), md_path)
    except Exception as e:
        check("2. .md file written", False, str(e))
        print_summary()
        return

    # ---------- 3. Page boundaries preserved ----------
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    header_matches = re.findall(r"^# Page (\d+)\s*$", md_content, flags=re.MULTILINE)
    header_nums = [int(n) for n in header_matches]
    expected_nums = [n for n, _ in normalized_pages]
    check("3. Page headers present", len(header_nums) == len(normalized_pages),
          f"found {len(header_nums)} headers, expected {len(normalized_pages)}")
    check("3a. Page headers in correct order", header_nums == sorted(header_nums),
          f"{header_nums}")
    check("3b. Page numbers match extraction", header_nums == expected_nums,
          f"md={header_nums} vs extracted={expected_nums}")

    # ---------- 4. Content fidelity: markdown vs originally extracted text ----------
    md_pages_inline = parse_markdown_pages(
        md_path,
        os.path.basename(pdf_path)
    )
    
    md_lookup = {
        page["page"]: page["text"]
        for page in md_pages_inline
    }

    exact_mismatches = []
    ws_normalized_mismatches = []
    for page_num, original_text in normalized_pages:
        md_text = md_lookup.get(page_num)
        if md_text != original_text:
            exact_mismatches.append(page_num)
            if normalize_ws(md_text) != normalize_ws(original_text):
                ws_normalized_mismatches.append(page_num)

    check("4. Markdown content byte-exact vs extraction", len(exact_mismatches) == 0,
          f"mismatched pages (any diff): {exact_mismatches}")
    check("4a. Markdown content matches ignoring leading/trailing newlines",
          len(ws_normalized_mismatches) == 0,
          f"mismatched pages (real content diff, not just whitespace): {ws_normalized_mismatches}")

    # ---------- 5. parse_markdown_pages() output shape matches chunker's expectation ----------
    # NOTE: per your update, parse_markdown_pages should return page DICTS
    # ({"text":..., "source":..., "page":...}), not tuples. Re-checking that here
    # explicitly since the shape matters for step 6.
    try:
        # If parse_markdown_pages truly returns dicts now, this reflects it directly.
        # If it still returns tuples (as in the earlier draft), this test will show that.
        raw_parsed = parse_markdown_pages(md_path, os.path.basename(pdf_path))
        if raw_parsed and isinstance(raw_parsed[0], dict):
            shape_ok = all({"text", "source", "page"} <= set(p.keys()) for p in raw_parsed)
            check("5. parse_markdown_pages returns chunker-expected dicts", shape_ok,
                  f"sample keys: {list(raw_parsed[0].keys())}")
            pages_for_chunker = raw_parsed
        else:
            check("5. parse_markdown_pages returns chunker-expected dicts", False,
                  "Currently returns tuples, not dicts -- chunk_text() call below will likely fail or misbehave.")
            # Best-effort shim so the rest of the test can still run
            pages_for_chunker = [
                {"text": t, "source": os.path.basename(pdf_path), "page": n}
                for n, t in raw_parsed
            ]
    except Exception as e:
        check("5. parse_markdown_pages returns chunker-expected dicts", False, str(e))
        pages_for_chunker = []

    # ---------- 6. Chunking still works ----------
    try:
        chunks = chunk_text(pages_for_chunker)
        chunks_ok = isinstance(chunks, list) and len(chunks) > 0
        check("6. chunk_text() produces chunks", chunks_ok, f"{len(chunks)} chunks")
        if chunks_ok:
            sample = chunks[0]
            check("6a. Chunks carry page metadata",
                  any(k in sample for k in ("page", "page_num")),
                  f"sample chunk keys: {list(sample.keys()) if isinstance(sample, dict) else type(sample)}")
    except Exception as e:
        check("6. chunk_text() produces chunks", False, str(e))
        chunks = []

    # ---------- 7. Embeddings / FAISS ----------
    # Left as a manual step since indexer.py's full orchestration function name
    # wasn't specified. Uncomment and adjust once you confirm the function:
    #
    # from src.indexer import process_and_index_pdf
    # try:
    #     process_and_index_pdf(pdf_path)
    #     check("7. Full indexer.py pipeline runs end-to-end", True)
    # except Exception as e:
    #     check("7. Full indexer.py pipeline runs end-to-end", False, str(e))
    print("[SKIP] 7. Embeddings/FAISS -- run your normal upload/index flow manually and "
          "confirm no exceptions; wire in process_and_index_pdf() above once you confirm its name.")

    # ---------- 8. Manual verification helper: find date-range-like patterns ----------
    print("\n=== Date-range patterns found in Markdown (for manual '1880-1940' style checks) ===")
    pattern = re.compile(r"\b(1[5-9]\d{2}|20\d{2})\s*[-–—]\s*(1[5-9]\d{2}|20\d{2})\b")
    found_any = False
    current_page = None
    for line in md_content.split("\n"):
        header_match = re.match(r"^# Page (\d+)\s*$", line)
        if header_match:
            current_page = int(header_match.group(1))
            continue
        for m in pattern.finditer(line):
            found_any = True
            print(f"  page {current_page}: '{m.group(0)}'  (context: ...{line.strip()[:80]}...)")
    if not found_any:
        print("  (none found in this PDF -- test on a PDF known to contain a date range)")

    print(f"\nMarkdown file to open and eyeball manually: {md_path}")

    print_summary()


def print_summary():
    print("\n=== Summary ===")
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    print(f"{passed}/{total} checks passed")
    failed = [n for n, p, _ in results if not p]
    if failed:
        print("Failed checks:")
        for n in failed:
            print(f"  - {n}")


if __name__ == "__main__":
    main()