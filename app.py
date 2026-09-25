import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from src.indexer import build_index_from_uploads, load_existing_index
from src.embeddings import embed_query
from src.llm import generate_answer
from src.rag import answer_question
from src.feedback import init_db, log_interaction, record_feedback
from src.md_converter import markdown_already_exists

load_dotenv()

app = Flask(__name__)

UPLOAD_DIR = os.path.join("data", "uploads")
MARKDOWN_DIR = os.path.abspath(os.path.join(UPLOAD_DIR, "..", "markdown"))
VECTOR_STORE_DIR = "vector_store"
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss.index")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.pkl")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
init_db()


# Load previously built index on startup
vector_store = load_existing_index(INDEX_PATH, METADATA_PATH)

processed_files = (
    sorted(set(c["source"] for c in vector_store.metadata))
    if vector_store else []
)

processed_file_count = len(processed_files)


@app.route("/")
def index():
    return render_template(
        "index.html",
        processed_file_count=processed_file_count,
        processed_files=processed_files
    )

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(
        os.path.abspath(UPLOAD_DIR),
        secure_filename(filename),
        mimetype="application/pdf"
    )

@app.route("/upload", methods=["POST"])
def upload():
    global vector_store, processed_file_count, processed_files

    files = request.files.getlist("pdf_files")

    if not files or files[0].filename == "":
        return render_template(
            "index.html",
            processed_file_count=processed_file_count,
            processed_files=processed_files,
            upload_message="No files selected."
        )

    saved_count = 0

    for file in files:
        if file.filename.lower().endswith(".pdf"):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_DIR, filename))
            saved_count += 1

    if saved_count == 0:
        return render_template(
            "index.html",
            processed_file_count=processed_file_count,
            processed_files=processed_files,
            upload_message="No valid PDF files were uploaded."
        )

    result = build_index_from_uploads(
        UPLOAD_DIR,
        INDEX_PATH,
        METADATA_PATH
    )

    if result["store"] is None:
        return render_template(
            "index.html",
            processed_file_count=processed_file_count,
            processed_files=processed_files,
            upload_message="Upload succeeded but no extractable text was found."
        )

    vector_store = result["store"]

    processed_files = sorted(
        set(c["source"] for c in vector_store.metadata)
    )

    processed_file_count = len(processed_files)

    if result["new_files"] > 0:
        message = (
            f"{result['new_files']} new document(s) processed "
            f"({result['new_chunks']} new chunks indexed). "
            f"{processed_file_count} document(s) total."
        )
    else:
        message = "No new documents to process (already indexed)."

    return render_template(
        "index.html",
        processed_file_count=processed_file_count,
        processed_files=processed_files,
        upload_message=message
    )

def make_snippet(text, limit=240):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()

    if not question:
        return render_template(
            "index.html",
            processed_file_count=processed_file_count,
            processed_files=processed_files,
            ask_error="Please enter a question."
        )

    if vector_store is None:
        return render_template(
            "index.html",
            processed_file_count=processed_file_count,
            processed_files=processed_files,
            ask_error="No documents have been processed yet. Please upload a PDF first."
        )

    result = answer_question(
        question,
        vector_store,
        embed_query,
        generate_answer,
        top_k=3
    )

    interaction_id = log_interaction(
        question,
        result["answer"],
        result["sources"],
        result["low_confidence"]
    )

    display_sources = []

    if not result["low_confidence"]:
        display_sources = [
            {**src, "snippet": make_snippet(chunk["text"])}
            for src, (chunk, _score) in zip(
                result["sources"],
                result["retrieved"]
            )
        ]

    return render_template(
        "index.html",
        processed_file_count=processed_file_count,
        processed_files=processed_files,
        question=question,
        answer=result["answer"],
        sources=display_sources,
        low_confidence=result["low_confidence"],
        interaction_id=interaction_id
    )

@app.route("/delete/<path:filename>", methods=["POST"])
def delete_document(filename):
    global vector_store, processed_files, processed_file_count

    # Match against the source names actually stored in the index.
    indexed_sources = (
        set(c["source"] for c in vector_store.metadata)
        if vector_store else set()
    )
    source = filename if filename in indexed_sources else secure_filename(filename)

    # Must be a plain file name: no folders, not empty.
    if not source or os.path.basename(source) != source:
        return jsonify({"success": False, "error": "Invalid filename."}), 400

    # Remove vectors + metadata, then persist the index and metadata.pkl
    removed = 0
    if vector_store is not None:
        removed = vector_store.remove_by_source(source)
        if removed:
            vector_store.save(INDEX_PATH, METADATA_PATH)

    # Delete the uploaded PDF
    pdf_path = os.path.join(UPLOAD_DIR, source)
    pdf_deleted = os.path.isfile(pdf_path)
    if pdf_deleted:
        os.remove(pdf_path)

    # Delete only this document's Markdown file (path rule comes from md_converter)
    md_exists, md_path = markdown_already_exists(source, MARKDOWN_DIR)
    md_deleted = bool(md_exists and md_path and os.path.isfile(md_path))
    if md_deleted:
        os.remove(md_path)

    processed_files = (
        sorted(set(c["source"] for c in vector_store.metadata))
        if vector_store else []
    )
    processed_file_count = len(processed_files)

    if not (removed or pdf_deleted or md_deleted):
        return jsonify({
            "success": False,
            "error": "Document not found.",
            "processed_file_count": processed_file_count
        }), 404

    return jsonify({
        "success": True,
        "filename": source,
        "processed_file_count": processed_file_count
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    interaction_id = request.form.get("interaction_id")
    vote = request.form.get("vote")

    if interaction_id and vote in ("helpful", "not_helpful"):
        record_feedback(int(interaction_id), vote)

    return render_template(
        "index.html",
        processed_file_count=processed_file_count,
        processed_files=processed_files,
        feedback_message="Thanks for your feedback!"
    )




if __name__ == "__main__":
    print("GEMINI_API_KEY loaded:", bool(os.getenv("GEMINI_API_KEY")))
    app.run(debug=True)