// Render the Markdown answer returned by the LLM instead of showing raw asterisks
document.addEventListener("DOMContentLoaded", () => {
    const raw = document.getElementById("answer-raw");
    const target = document.getElementById("answer-content");
    if (raw && target && window.marked) {
        const text = JSON.parse(raw.textContent);
        target.innerHTML = marked.parse(text);
    }

    // Show selected file names instead of the default browser label
    const fileInput = document.getElementById("pdf_files");
    const fileText = document.getElementById("file-drop-text");
    if (fileInput && fileText) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length === 0) {
                fileText.textContent = "Click to choose PDF files";
            } else if (fileInput.files.length === 1) {
                fileText.textContent = fileInput.files[0].name;
            } else {
                fileText.textContent = `${fileInput.files.length} files selected`;
            }
        });
    }

    // Give quick feedback that the question is processing (page still reloads on submit)
    const askForm = document.getElementById("ask-form");
    const askBtn = document.getElementById("ask-btn");
    if (askForm && askBtn) {
        askForm.addEventListener("submit", () => {
            askBtn.textContent = "Thinking…";
            askBtn.disabled = true;
        });
    }
});