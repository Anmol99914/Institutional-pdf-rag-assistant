import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from src.indexer import build_index_from_uploads, load_existing_index
from src.embeddings import embed_query
from src.llm import generate_answer
from src.rag import answer_question
from src.feedback import init_db, log_interaction, record_feedback


load_dotenv()

app = Flask(__name__)

UPLOAD_DIR = os.path.join("data", "uploads")
VECTOR_STORE_DIR = "vector_store"
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss.index")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.pkl")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
init_db()

# Load a previously built index on startup, if one exists
vector_store = load_existing_index(INDEX_PATH, METADATA_PATH)
processed_file_count = len(set(c["source"] for c in vector_store.metadata)) if vector_store else 0


@app.route("/")
def index():
    return render_template("index.html", processed_file_count=processed_file_count)
        
@app.route("/upload", methods=["POST"])
def upload():
    global vector_store, processed_file_count

    files = request.files.getlist("pdf_files")
    if not files or files[0].filename == "":
        return render_template("index.html", processed_file_count=processed_file_count,
                                upload_message="No files selected.")

    saved_count = 0
    for file in files:
        if file.filename.lower().endswith(".pdf"):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_DIR, filename))
            saved_count += 1

    if saved_count == 0:
        return render_template("index.html", processed_file_count=processed_file_count,
                                upload_message="No valid PDF files were uploaded.")

    result = build_index_from_uploads(UPLOAD_DIR, INDEX_PATH, METADATA_PATH)

    if result["store"] is None:
        return render_template("index.html", processed_file_count=processed_file_count,
                                upload_message="Upload succeeded but no extractable text was found.")

    vector_store = result["store"]
    processed_file_count = result["total_files"]

    if result["new_files"] > 0:
        message = (f"{result['new_files']} new document(s) processed "
                   f"({result['new_chunks']} new chunks indexed). "
                   f"{result['total_files']} document(s) total.")
    else:
        message = "No new documents to process (already indexed)."

    return render_template("index.html", processed_file_count=processed_file_count,
                            upload_message=message)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()

    if not question:
        return render_template("index.html", processed_file_count=processed_file_count,
                                ask_error="Please enter a question.")

    if vector_store is None:
        return render_template("index.html", processed_file_count=processed_file_count,
                                ask_error="No documents have been processed yet. Please upload a PDF first.")

    result = answer_question(question, vector_store, embed_query, generate_answer, top_k=3)

    interaction_id = log_interaction(question, result["answer"], result["sources"], result["low_confidence"])

    return render_template("index.html", processed_file_count=processed_file_count,
                            question=question, answer=result["answer"],
                            sources=result["sources"], low_confidence=result["low_confidence"],
                            interaction_id=interaction_id)

@app.route("/feedback", methods=["POST"])
def feedback():
    interaction_id = request.form.get("interaction_id")
    vote = request.form.get("vote")  # "helpful" or "not_helpful"

    if interaction_id and vote in ("helpful", "not_helpful"):
        record_feedback(int(interaction_id), vote)

    return render_template("index.html", processed_file_count=processed_file_count,
                            feedback_message="Thanks for your feedback!")


if __name__ == "__main__":
    print("GEMINI_API_KEY loaded:", bool(os.getenv("GEMINI_API_KEY")))
    app.run(debug=True)