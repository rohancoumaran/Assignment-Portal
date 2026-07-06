# Student Assignment Upload Portal

Flask backend with an HTML, CSS, and JavaScript frontend.

## Run

```powershell
cd R:\Cloud\assignment_portal
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Endpoints

```text
POST /upload
GET /files
GET /download/<filename>
```

Uploaded files are stored in:

```text
R:\Cloud\assignment_portal\uploads
```
