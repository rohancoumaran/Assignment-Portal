from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename


app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".txt",
    ".zip",
}


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/upload")
def upload_file():
    uploaded_file = request.files.get("assignment")
    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({"error": "Please choose a file to upload."}), 400

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        return jsonify({"error": "Invalid filename."}), 400

    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Unsupported file type."}), 400

    uploaded_file.save(UPLOAD_DIR / filename)
    return jsonify({"message": "Assignment uploaded successfully.", "filename": filename}), 201


@app.get("/files")
def list_files():
    files = sorted(path.name for path in UPLOAD_DIR.iterdir() if path.is_file())
    return jsonify({"files": files})


@app.get("/download/<path:filename>")
def download_file(filename):
    safe_name = secure_filename(filename)
    return send_from_directory(UPLOAD_DIR, safe_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
