"""
test_markdown_pipeline.py

End-to-end verification of the PDF -> Markdown -> chunk -> embed -> FAISS
pipeline.

Run from your project root with the dsml312 environment active:

    python test_markdown_pipeline.py path/to/sample.pdf

This does NOT modify your existing pipeline. It calls your real modules
and reports pass/fail per stage so you can tell exactly where a problem
lives if something's wrong.
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pdf_processor import extract_text_from_pdf
from src.md_converter import (
    pdf_pages_to_markdown,
    parse_markdown_pages,
    markdown_already_exists
)
from src.chunker import chunk_text


MARKDOWN_DIR = os.path.join("data", "markdown")

results = []


def check(name, passed, detail=""):
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}" + (f" -- {detail}" if detail else ""))


def normalize_ws(s):
    """Only remove leading/trailing newlines for comparison."""
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

    # ============================================================
    # 1. PDF EXTRACTION
    # ============================================================

    try:
        pages = extract_text_from_pdf(pdf_path)

        check(
            "1. PyMuPDF extraction runs",
            True,
            f"{len(pages)} pages returned"
        )

    except Exception as e:

        check(
            "1. PyMuPDF extraction runs",
            False,
            str(e)
        )

        print_summary()
        return

    # ============================================================
    # 1A. NORMALIZE EXTRACTION OUTPUT
    # ============================================================
    #
    # pdf_pages_to_markdown() expects dictionaries:
    #
    # {
    #     "page": 1,
    #     "text": "..."
    # }
    #
    # Some extraction versions may return tuples instead, so this
    # test converts either format into the dictionary structure.
    # ============================================================

    normalized_pages = []

    for i, p in enumerate(pages, start=1):

        if isinstance(p, dict):

            normalized_pages.append({
                "page": p.get("page", i),
                "text": p.get("text", "")
            })

        elif isinstance(p, tuple):

            page_num, text = p

            normalized_pages.append({
                "page": page_num,
                "text": text
            })

        else:

            normalized_pages.append({
                "page": i,
                "text": str(p)
            })

    total_chars_extracted = sum(
        len(p["text"])
        for p in normalized_pages
    )

    empty_pages = [
        p["page"]
        for p in normalized_pages
        if not p["text"] or not p["text"].strip()
    ]

    check(
        "1a. Non-trivial text extracted",
        total_chars_extracted > 0,
        f"total_chars={total_chars_extracted}, "
        f"empty_pages={empty_pages}"
    )

    # ============================================================
    # 2. MARKDOWN FILE PRODUCED
    # ============================================================

    try:

        md_path, stage_meta = pdf_pages_to_markdown(
            normalized_pages,
            pdf_path,
            MARKDOWN_DIR
        )

        check(
            "2. .md file written",
            os.path.exists(md_path),
            md_path
        )

    except Exception as e:

        check(
            "2. .md file written",
            False,
            str(e)
        )

        print_summary()
        return

    # ============================================================
    # 3. PAGE BOUNDARIES PRESERVED
    # ============================================================

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    header_matches = re.findall(
        r"^# Page (\d+)\s*$",
        md_content,
        flags=re.MULTILINE
    )

    header_nums = [
        int(n)
        for n in header_matches
    ]

    expected_nums = [
        p["page"]
        for p in normalized_pages
    ]

    check(
        "3. Page headers present",
        len(header_nums) == len(normalized_pages),
        f"found {len(header_nums)} headers, "
        f"expected {len(normalized_pages)}"
    )

    check(
        "3a. Page headers in correct order",
        header_nums == sorted(header_nums),
        f"{header_nums}"
    )

    check(
        "3b. Page numbers match extraction",
        header_nums == expected_nums,
        f"md={header_nums} vs extracted={expected_nums}"
    )

    # ============================================================
    # 4. MARKDOWN CONTENT FIDELITY
    # ============================================================

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

    for page in normalized_pages:

        page_num = page["page"]
        original_text = page["text"]

        md_text = md_lookup.get(page_num)

        if md_text != original_text:

            exact_mismatches.append(page_num)

            if normalize_ws(md_text) != normalize_ws(original_text):
                ws_normalized_mismatches.append(page_num)

    check(
        "4. Markdown content byte-exact vs extraction",
        len(exact_mismatches) == 0,
        f"mismatched pages (any diff): {exact_mismatches}"
    )

    check(
        "4a. Markdown content matches ignoring "
        "leading/trailing newlines",
        len(ws_normalized_mismatches) == 0,
        "mismatched pages "
        f"(real content diff, not just whitespace): "
        f"{ws_normalized_mismatches}"
    )

    # ============================================================
    # 5. PARSE MARKDOWN OUTPUT SHAPE
    # ============================================================

    try:

        raw_parsed = parse_markdown_pages(
            md_path,
            os.path.basename(pdf_path)
        )

        if raw_parsed and isinstance(raw_parsed[0], dict):

            shape_ok = all(
                {"text", "source", "page"} <= set(p.keys())
                for p in raw_parsed
            )

            check(
                "5. parse_markdown_pages returns "
                "chunker-expected dicts",
                shape_ok,
                f"sample keys: {list(raw_parsed[0].keys())}"
            )

            pages_for_chunker = raw_parsed

        else:

            check(
                "5. parse_markdown_pages returns "
                "chunker-expected dicts",
                False,
                "Currently returns tuples, not dicts."
            )

            # Best-effort compatibility shim
            pages_for_chunker = [
                {
                    "text": t,
                    "source": os.path.basename(pdf_path),
                    "page": n
                }
                for n, t in raw_parsed
            ]

    except Exception as e:

        check(
            "5. parse_markdown_pages returns "
            "chunker-expected dicts",
            False,
            str(e)
        )

        pages_for_chunker = []

    # ============================================================
    # 6. CHUNKING
    # ============================================================

    try:

        chunks = chunk_text(pages_for_chunker)

        chunks_ok = (
            isinstance(chunks, list)
            and len(chunks) > 0
        )

        check(
            "6. chunk_text() produces chunks",
            chunks_ok,
            f"{len(chunks)} chunks"
        )

        if chunks_ok:

            sample = chunks[0]

            check(
                "6a. Chunks carry page metadata",
                isinstance(sample, dict)
                and any(
                    k in sample
                    for k in ("page", "page_num")
                ),
                f"sample chunk keys: "
                f"{list(sample.keys()) if isinstance(sample, dict) else type(sample)}"
            )

    except Exception as e:

        check(
            "6. chunk_text() produces chunks",
            False,
            str(e)
        )

        chunks = []

    # ============================================================
    # 7. EMBEDDINGS / FAISS
    # ============================================================
    #
    # This remains a manual step because the exact orchestration
    # function in indexer.py has not yet been confirmed.
    # ============================================================

    print(
        "[SKIP] 7. Embeddings/FAISS -- run your normal "
        "upload/index flow manually and confirm no exceptions."
    )

    # ============================================================
    # 8. DATE-RANGE VERIFICATION
    # ============================================================

    print(
        "\n=== Date-range patterns found in Markdown "
        "(for manual '1880-1940' style checks) ==="
    )

    pattern = re.compile(
        r"\b(1[5-9]\d{2}|20\d{2})\s*[-–—]\s*"
        r"(1[5-9]\d{2}|20\d{2})\b"
    )

    found_any = False
    current_page = None

    for line in md_content.split("\n"):

        header_match = re.match(
            r"^# Page (\d+)\s*$",
            line
        )

        if header_match:

            current_page = int(
                header_match.group(1)
            )

            continue

        for m in pattern.finditer(line):

            found_any = True

            print(
                f"  page {current_page}: "
                f"'{m.group(0)}' "
                f"(context: ...{line.strip()[:80]}...)"
            )

    if not found_any:

        print(
            "  (none found in this PDF -- test on a PDF "
            "known to contain a date range)"
        )

    print(
        f"\nMarkdown file to open and eyeball manually: "
        f"{md_path}"
    )

    # ============================================================
    # SUMMARY
    # ============================================================

    print_summary()


def print_summary():

    print("\n=== Summary ===")

    passed = sum(
        1
        for _, p, _ in results
        if p
    )

    total = len(results)

    print(
        f"{passed}/{total} checks passed"
    )

    failed = [
        n
        for n, p, _
        in results
        if not p
    ]

    if failed:

        print("Failed checks:")

        for n in failed:
            print(f"  - {n}")


if __name__ == "__main__":
    main()