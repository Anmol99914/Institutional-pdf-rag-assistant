"""
md_converter.py

Serializes PyMuPDF-extracted, page-aware text into a Markdown file
BEFORE chunking, so extraction accuracy can be manually verified.

Design rules (per project requirement):
- No text cleanup, dehyphenation, whitespace normalization, or "fixing".
- The .md file must represent exactly what PyMuPDF extracted, so a user
  can open it and check whether e.g. "1880-1940" was extracted intact.
- Page boundaries are marked with literal '# Page N' headers so the
  chunker (and a user reader) can locate page breaks unambiguously.
"""

import os
import logging
import re

logger = logging.getLogger("markdown_stage")

PAGE_HEADER_RE = re.compile(r"^# Page (\d+)\s*$")


def pdf_pages_to_markdown(pages, source_filename, markdown_dir):
    """
    Convert already-extracted PDF pages into a verifiable Markdown file.

    Args:
        pages: list of (page_num, text) tuples, 1-indexed, as produced by
               the existing PyMuPDF extraction step. This function does
               NOT re-extract from the PDF -- it serializes what was
               already extracted, so the .md is a faithful mirror of
               extraction output.
        source_filename: original PDF filename (used to name the .md file
               and to keep extraction <-> markdown <-> chunk traceable).
        markdown_dir: directory where .md files are stored.

    Returns:
        md_path: path to the written .md file.
        stage_meta: dict of debug info about this conversion step
                    (per-page char counts, total pages, byte size).
    """
    os.makedirs(markdown_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(source_filename))[0]
    md_path = os.path.join(markdown_dir, f"{base_name}.md")

    per_page_stats = []
    lines = []

    for page_entry in pages:
        page_num = page_entry["page"]
        text = page_entry.get("text")

        # Verbatim text -- do not strip, dehyphenate, or normalize.
        # If PyMuPDF returned nothing (blank/scanned page), that empty
        # string is preserved as-is so it's visible in the .md, not
        # silently dropped or replaced with a placeholder.
        lines.append(f"# Page {page_num}")
        lines.append("")
        lines.append(text if text is not None else "")
        lines.append("")

        per_page_stats.append({
            "page": page_num,
            "char_count": len(text) if text else 0,
            "is_empty": not bool(text and text.strip()),
        })

    md_content = "\n".join(lines)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    stage_meta = {
        "source_pdf": source_filename,
        "md_path": md_path,
        "total_pages": len(pages),
        "total_chars": sum(p["char_count"] for p in per_page_stats),
        "empty_pages": [p["page"] for p in per_page_stats if p["is_empty"]],
        "byte_size": os.path.getsize(md_path),
        "per_page": per_page_stats,
    }

    empty_ct = len(stage_meta["empty_pages"])
    logger.info(
        "markdown_written file=%s pages=%d chars=%d empty_pages=%d",
        md_path, stage_meta["total_pages"], stage_meta["total_chars"], empty_ct,
    )
    if empty_ct:
        logger.warning(
            "markdown has empty pages (likely scanned/image pages, no OCR run): %s",
            stage_meta["empty_pages"],
        )

    return md_path, stage_meta

def parse_markdown_pages(md_path, source_filename):
    """
    Read a previously-written Markdown file and convert it back into
    the same page-data structure expected by the existing chunker.

    Returns:
        list of dicts:
        {
            "text": str,
            "source": str,
            "page": int
        }
    """
    if not os.path.exists(md_path):
        raise FileNotFoundError(f"Markdown source not found: {md_path}")

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    pages = []
    current_page_num = None
    current_lines = []

    def flush():
        if current_page_num is not None:
            text = "\n".join(current_lines).strip("\n")

            pages.append({
                "text": text,
                "source": source_filename,
                "page": current_page_num
            })

    for line in lines:
        match = PAGE_HEADER_RE.match(line)

        if match:
            flush()
            current_page_num = int(match.group(1))
            current_lines = []
        else:
            current_lines.append(line)

    flush()

    logger.info(
        "markdown_parsed file=%s pages=%d",
        md_path,
        len(pages)
    )

    return pages


def markdown_already_exists(source_filename, markdown_dir):
    """Used by incremental indexing to skip re-writing an existing .md."""
    base_name = os.path.splitext(os.path.basename(source_filename))[0]
    md_path = os.path.join(markdown_dir, f"{base_name}.md")
    return os.path.exists(md_path), md_path