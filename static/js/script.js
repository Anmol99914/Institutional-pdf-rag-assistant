document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const desktopQuery = window.matchMedia("(min-width: 992px)");
    const isDesktop = () => desktopQuery.matches;

    /* ------------------------------------------------------------
       1. Render the Markdown answer returned by the LLM
       ------------------------------------------------------------ */
    const raw = document.getElementById("answer-raw");
    const answerTarget = document.getElementById("answer-content");
    if (raw && answerTarget) {
    const text = JSON.parse(raw.textContent);

    if (window.marked) {
        answerTarget.innerHTML = marked.parse(text);

        // Render mathematical expressions such as $$...$$ using MathJax
        if (window.MathJax) {
            MathJax.typesetPromise([answerTarget]).catch((err) => {
                console.error("MathJax rendering error:", err);
            });
        }
    } else {
        // marked.js is loaded from a CDN; if it is unreachable, still show the answer
        answerTarget.textContent = text;
        answerTarget.classList.add("plain");
    }
}

    /* ------------------------------------------------------------
       2. Sidebar (collapsible on desktop, drawer on smaller screens)
       ------------------------------------------------------------ */
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarOverlay = document.getElementById("sidebar-overlay");

    function sidebarIsOpen() {
        return isDesktop()
            ? !body.classList.contains("sidebar-collapsed")
            : body.classList.contains("sidebar-open");
    }

    function setSidebar(open) {
        if (isDesktop()) {
            body.classList.toggle("sidebar-collapsed", !open);
        } else {
            body.classList.toggle("sidebar-open", open);
        }
        sidebarToggle.setAttribute("aria-expanded", String(open));
    }

    function toggleSidebar() {
        setSidebar(!sidebarIsOpen());
    }

    sidebarToggle.addEventListener("click", toggleSidebar);
    sidebarOverlay.addEventListener("click", () => setSidebar(false));
    desktopQuery.addEventListener("change", () => {
        body.classList.remove("sidebar-open");
        sidebarToggle.setAttribute("aria-expanded", String(sidebarIsOpen()));
    });
    sidebarToggle.setAttribute("aria-expanded", String(sidebarIsOpen()));

    /* ------------------------------------------------------------
       3. View switching (Ask / Upload / Processed Documents / Help)
       ------------------------------------------------------------ */
    const viewPanels = document.querySelectorAll("[data-view-panel]");
    const navItems = document.querySelectorAll(".nav-item");

    function switchView(name) {
        viewPanels.forEach((panel) => {
            panel.hidden = panel.dataset.viewPanel !== name;
        });
        navItems.forEach((item) => {
            if (item.dataset.view === name) {
                item.setAttribute("aria-current", "page");
            } else {
                item.removeAttribute("aria-current");
            }
        });
        if (!isDesktop()) setSidebar(false);
    }

    document.querySelectorAll("[data-view]").forEach((el) => {
        el.addEventListener("click", () => {
            switchView(el.dataset.view);
            window.scrollTo(0, 0);
        });
    });

    /* ------------------------------------------------------------
       4. Ask form: loading state, Enter to submit, example questions
       ------------------------------------------------------------ */
    const askForm = document.getElementById("ask-form");
    const askBtn = document.getElementById("ask-btn");
    const questionBox = document.getElementById("question");
    const loadingPanel = document.getElementById("loading-panel");

    if (askForm && askBtn && questionBox) {
        // Page still reloads on submit, so show progress while waiting for the answer
        askForm.addEventListener("submit", () => {
            askBtn.textContent = "Thinking…";
            askBtn.disabled = true;
            const results = document.getElementById("qa-results");
            const examples = document.getElementById("examples");
            if (results) results.hidden = true;
            if (examples) examples.hidden = true;
            if (loadingPanel) loadingPanel.hidden = false;
        });

        questionBox.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
                e.preventDefault();
                if (questionBox.value.trim()) askForm.requestSubmit();
            }
        });

        document.querySelectorAll(".chip").forEach((chip) => {
            chip.addEventListener("click", () => {
                questionBox.value = chip.dataset.question;
                questionBox.focus();
            });
        });
    }

    // Restore the form if the user returns via the browser's back button
    window.addEventListener("pageshow", (e) => {
        if (e.persisted && askBtn) {
            askBtn.textContent = "Ask";
            askBtn.disabled = false;
            if (loadingPanel) loadingPanel.hidden = true;
            const results = document.getElementById("qa-results");
            if (results) results.hidden = false;
        }
    });

    /* ------------------------------------------------------------
       5. PDF viewer: open the exact page of a cited source
       ------------------------------------------------------------ */
    const askLayout = document.getElementById("ask-layout");
    const viewerBody = document.getElementById("viewer-body");
    const viewerDoc = document.getElementById("viewer-doc");
    const viewerPage = document.getElementById("viewer-page");
    const viewerNewTab = document.getElementById("viewer-newtab");
    const viewerClose = document.getElementById("viewer-close");
    let activeSourceBtn = null;

    function openPdfViewer(filename, page, trigger) {
        const url = `/uploads/${encodeURIComponent(filename)}#page=${encodeURIComponent(page)}`;

        viewerDoc.textContent = filename;
        viewerPage.textContent = `Page ${page}`;
        viewerNewTab.href = url;

        // A new iframe is created each time: changing only the #page hash on an
        // existing iframe often does not make the browser jump to the new page.
        const frame = document.createElement("iframe");
        frame.title = `${filename}, page ${page}`;
        frame.src = url;
        viewerBody.replaceChildren(frame);

        askLayout.classList.add("viewer-open");

        if (activeSourceBtn) {
            activeSourceBtn.removeAttribute("aria-current");
            activeSourceBtn.closest(".source-card").classList.remove("active");
        }
        activeSourceBtn = trigger;
        if (trigger) {
            trigger.setAttribute("aria-current", "true");
            trigger.closest(".source-card").classList.add("active");
        }
        viewerClose.focus();
    }

    function closePdfViewer() {
        askLayout.classList.remove("viewer-open");
        viewerBody.replaceChildren();
        if (activeSourceBtn) {
            activeSourceBtn.removeAttribute("aria-current");
            activeSourceBtn.closest(".source-card").classList.remove("active");
            activeSourceBtn.focus();
            activeSourceBtn = null;
        }
    }

    document.querySelectorAll(".view-page-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            openPdfViewer(btn.dataset.filename, btn.dataset.page, btn);
        });
    });
    if (viewerClose) viewerClose.addEventListener("click", closePdfViewer);

    document.addEventListener("keydown", (e) => {
        if (e.key !== "Escape") return;
        if (askLayout && askLayout.classList.contains("viewer-open")) {
            closePdfViewer();
        } else if (!isDesktop() && body.classList.contains("sidebar-open")) {
            setSidebar(false);
        }
    });

    /* ------------------------------------------------------------
       6. Feedback: send without reloading so the answer stays on screen
       ------------------------------------------------------------ */
    const feedbackForm = document.getElementById("feedback-form");
    const feedbackStatus = document.getElementById("feedback-status");

    if (feedbackForm && feedbackStatus) {
        feedbackForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const vote = e.submitter ? e.submitter.value : null;
            if (!vote) return;

            const data = new FormData(feedbackForm);
            data.set("vote", vote);
            const buttons = feedbackForm.querySelectorAll("button");
            buttons.forEach((b) => (b.disabled = true));

            try {
                const response = await fetch("/feedback", { method: "POST", body: data });
                if (!response.ok) throw new Error("Feedback request failed");
                feedbackForm.hidden = true;
                feedbackStatus.textContent = "Thank you for your feedback.";
            } catch (err) {
                buttons.forEach((b) => (b.disabled = false));
                feedbackStatus.textContent = "Could not send feedback. Please try again.";
            }
        });
    }

    /* ------------------------------------------------------------
       7. Upload: file selection, drag and drop, processing state
       ------------------------------------------------------------ */
    const fileInput = document.getElementById("pdf_files");
    const fileText = document.getElementById("file-drop-text");
    const dropZone = document.getElementById("file-drop");
    const uploadForm = document.getElementById("upload-form");
    const uploadBtn = document.getElementById("upload-btn");

    if (fileInput && fileText) {
        const defaultText = fileText.textContent;

        const showSelection = () => {
            if (fileInput.files.length === 0) {
                fileText.textContent = defaultText;
            } else if (fileInput.files.length === 1) {
                fileText.textContent = fileInput.files[0].name;
            } else {
                fileText.textContent = `${fileInput.files.length} files selected`;
            }
        };

        fileInput.addEventListener("change", showSelection);

        if (dropZone) {
            ["dragenter", "dragover"].forEach((type) => {
                dropZone.addEventListener(type, (e) => {
                    e.preventDefault();
                    dropZone.classList.add("dragover");
                });
            });
            ["dragleave", "drop"].forEach((type) => {
                dropZone.addEventListener(type, (e) => {
                    e.preventDefault();
                    dropZone.classList.remove("dragover");
                });
            });
            dropZone.addEventListener("drop", (e) => {
                if (e.dataTransfer && e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    showSelection();
                }
            });
        }
    }

    if (uploadForm && uploadBtn) {
        uploadForm.addEventListener("submit", () => {
            uploadBtn.disabled = true;
            uploadBtn.textContent = "Processing documents…";
        });
    }

    /* ------------------------------------------------------------
       8. Processed documents: delete via fetch, no page reload
       ------------------------------------------------------------ */
    const docsBody = document.getElementById("docs-table-body");

    function updateCounts(count) {
        document.querySelectorAll(".processed-count").forEach((el) => {
            el.textContent = count;
        });
    }

    if (docsBody) {
        docsBody.addEventListener("click", async (e) => {
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
                    const row = docsBody.querySelector(`tr[data-filename="${CSS.escape(filename)}"]`);
                    if (row) row.remove();

                    updateCounts(data.processed_file_count);

                    if (data.processed_file_count === 0) {
                        docsBody.innerHTML =
                            '<tr class="empty-row"><td colspan="3">No documents uploaded yet.</td></tr>';
                    }

                    // An earlier upload message would now be out of date
                    const staleMsg = document.getElementById("upload-notice");
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

    /* ------------------------------------------------------------
       9. New question
       ------------------------------------------------------------ */
    const newQuestionBtn = document.getElementById("new-question-btn");

    if (newQuestionBtn) {
        newQuestionBtn.addEventListener("click", () => {
            window.location.href = "/";
        });
    }

    /* ------------------------------------------------------------
       Initial state
       ------------------------------------------------------------ */
    switchView(body.dataset.initialView || "ask");

    // After an answer loads, bring it into view (useful on small screens)
    const results = document.getElementById("qa-results");
    if (results) results.scrollIntoView({ block: "start" });
});