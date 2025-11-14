# OMR Web App

A full-stack Optical Mark Recognition (OMR) scanning system built with **FastAPI** and a lightweight HTML/CSS/JS frontend. Users upload an image of an OMR sheet, the backend auto-aligns, preprocesses, detects filled bubbles via OpenCV, and returns the answers (with confidence scores) as JSON.

## Project Structure

```
omr_webapp/
├── backend/
│   ├── main.py
│   ├── template.json
│   └── utils/
│       ├── preprocess.py
│       ├── detect.py
│       └── json_output.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── samples/
│   └── sample_omr.jpg
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick Start (Local)

```bash
cd omr_webapp
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the frontend by double-clicking `frontend/index.html` (or host it with any static HTTP server). Configure `frontend/app.js` to point to the deployed backend URL if different from `http://localhost:8000`.

## API

`POST /scan`

- Accepts `multipart/form-data` with `file` containing an image (`.png`, `.jpg`, `.jpeg`).
- Returns JSON:

```json
{
  "status": "success",
  "answers": {
    "1": {"choice": "B", "confidence": 0.91},
    "2": {"choice": "A", "confidence": 0.73}
  }
}
```

On failure the response contains `status: "error"` with a message.

## Deployment

### Docker

Build and run:

```bash
docker compose up --build
```

The backend listens on port `8000`. The frontend is served as static files by FastAPI at `/` for container deployments.

### Render.com / Railway.app

1. Push this repo to GitHub.
2. Create a new **Web Service**.
3. Use the Docker deployment option or set:
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
   - **Build Command**: `pip install -r requirements.txt`
4. Set the service port to 8000.

### AWS EC2 (Ubuntu)

```bash
sudo apt update && sudo apt install -y python3-venv
git clone <your repo>
cd omr_webapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Use Nginx or an ALB to expose port 8000 publicly.

## Logging

The backend writes logs to `backend/logs/app.log` and console. Rotate/ship as needed.

## Sample Asset

`samples/sample_omr.jpg` is a placeholder. Replace it with a real OMR sheet image to test detection.

