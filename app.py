import os
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request
from werkzeug.utils import secure_filename


load_dotenv()

app = Flask(__name__)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX", "assignments").strip("/")
AWS_REGION = os.getenv("AWS_REGION")
DOWNLOAD_URL_EXPIRES_IN = 300

s3_client = boto3.client("s3", region_name=AWS_REGION)

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


def s3_key(filename):
    if S3_PREFIX:
        return f"{S3_PREFIX}/{filename}"
    return filename


def s3_ready():
    return S3_BUCKET_NAME and S3_BUCKET_NAME != "your-s3-bucket-name"


def s3_not_configured_response():
    return jsonify({"error": "S3_BUCKET_NAME is not configured in .env."}), 500


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

    if not s3_ready():
        return s3_not_configured_response()

    try:
        s3_client.upload_fileobj(uploaded_file, S3_BUCKET_NAME, s3_key(filename))
    except (BotoCoreError, ClientError):
        return jsonify({"error": "Could not upload file to S3."}), 500

    return jsonify({"message": "Assignment uploaded to S3 successfully.", "filename": filename}), 201


@app.get("/files")
def list_files():
    if not s3_ready():
        return s3_not_configured_response()

    prefix = f"{S3_PREFIX}/" if S3_PREFIX else ""

    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix)
        files = []
        for page in pages:
            for item in page.get("Contents", []):
                key = item["Key"]
                if key.endswith("/"):
                    continue
                files.append(key.removeprefix(prefix))
    except (BotoCoreError, ClientError):
        return jsonify({"error": "Could not load files from S3."}), 500

    return jsonify({"files": sorted(files)})


@app.get("/download/<path:filename>")
def download_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({"error": "Invalid filename."}), 400

    if not s3_ready():
        return s3_not_configured_response()

    try:
        download_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET_NAME,
                "Key": s3_key(safe_name),
                "ResponseContentDisposition": f'attachment; filename="{safe_name}"',
            },
            ExpiresIn=DOWNLOAD_URL_EXPIRES_IN,
        )
    except (BotoCoreError, ClientError):
        return jsonify({"error": "Could not create S3 download link."}), 500

    return redirect(download_url)


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG") == "1",
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
    )
