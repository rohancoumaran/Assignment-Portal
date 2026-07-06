const uploadForm = document.querySelector("#uploadForm");
const fileInput = document.querySelector("#assignmentFile");
const selectedFile = document.querySelector("#selectedFile");
const statusMessage = document.querySelector("#statusMessage");
const fileList = document.querySelector("#fileList");
const fileCount = document.querySelector("#fileCount");
const refreshButton = document.querySelector("#refreshButton");

fileInput.addEventListener("change", () => {
  selectedFile.textContent = fileInput.files[0]?.name || "PDF, DOCX, PPTX, XLSX, TXT, or ZIP";
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!fileInput.files.length) {
    setStatus("Please choose a file first.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("assignment", fileInput.files[0]);
  setStatus("Uploading...", "pending");

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Upload failed.");
    }

    uploadForm.reset();
    selectedFile.textContent = "PDF, DOCX, PPTX, XLSX, TXT, or ZIP";
    setStatus(result.message, "success");
    await loadFiles();
  } catch (error) {
    setStatus(error.message, "error");
  }
});

refreshButton.addEventListener("click", loadFiles);

async function loadFiles() {
  fileList.innerHTML = '<p class="empty">Loading files...</p>';

  try {
    const response = await fetch("/files");
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Could not load files.");
    }

    renderFiles(result.files);
  } catch (error) {
    fileList.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
    fileCount.textContent = "0 files";
  }
}

function renderFiles(files) {
  fileCount.textContent = `${files.length} ${files.length === 1 ? "file" : "files"}`;

  if (!files.length) {
    fileList.innerHTML = '<p class="empty">No assignments uploaded yet.</p>';
    return;
  }

  fileList.innerHTML = files
    .map((filename) => {
      const safeName = escapeHtml(filename);
      const encodedName = encodeURIComponent(filename);
      return `
        <article class="file-row">
          <span title="${safeName}">${safeName}</span>
          <a class="download-button" href="/download/${encodedName}">Download</a>
        </article>
      `;
    })
    .join("");
}

function setStatus(message, type) {
  statusMessage.textContent = message;
  statusMessage.dataset.type = type;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[character];
  });
}

loadFiles();
