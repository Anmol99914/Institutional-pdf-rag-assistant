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

    // Documents management panel (gear icon)
    const gearBtn = document.getElementById("docs-gear-btn");
    const docsPanel = document.getElementById("docs-panel");
    const docsOverlay = document.getElementById("docs-panel-overlay");
    const panelClose = document.getElementById("docs-panel-close");

    const openPanel = () => {
        docsPanel.classList.add("open");
        docsOverlay.classList.add("open");
    };
    const closePanel = () => {
        docsPanel.classList.remove("open");
        docsOverlay.classList.remove("open");
    };

    if (gearBtn) gearBtn.addEventListener("click", openPanel);
    if (panelClose) panelClose.addEventListener("click", closePanel);
    if (docsOverlay) docsOverlay.addEventListener("click", closePanel);

        // Documents management: delete via fetch, update DOM instantly, no page reload
    const docsList = document.getElementById("docs-panel-list");
    const countEl = document.getElementById("processed-count-num");

    if (docsList) {
        docsList.addEventListener("click", async (e) => {
            const btn = e.target.closest(".delete-btn");
            if (!btn) return;

            const filename = btn.dataset.filename;
            if (!confirm(`Remove "${filename}" from the index?`)) return;

            btn.disabled = true;

            try {
                const response = await fetch(`/delete/${encodeURIComponent(filename)}`, {
                    method: "POST"
                });
                const data = await response.json();

                if (data.success) {
                    const li = docsList.querySelector(`li[data-filename="${CSS.escape(filename)}"]`);
                    if (li) li.remove();

                    if (countEl) countEl.textContent = data.processed_file_count;

                    if (data.processed_file_count === 0) {
                        docsList.innerHTML = '<li class="empty">No documents uploaded yet.</li>';
                    }
			const staleMsg = document.querySelector(".status-message.success");
    			if (staleMsg) staleMsg.remove();
                } else {
                    alert("Could not remove the document.");
                    btn.disabled = false;
                }
            } catch (err) {
                alert("Could not remove the document.");
                btn.disabled = false;
            }
        });
    }
});