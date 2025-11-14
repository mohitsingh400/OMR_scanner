# OMR Web App

A full-stack Optical Mark Recognition (OMR) scanning system built with **FastAPI** and a lightweight HTML/CSS/JS frontend. Users upload an image of an OMR sheet, the backend auto-aligns, preprocesses, detects filled bubbles via OpenCV, evaluates answers against an answer key, and returns the results with scoring as JSON.

## Features

- ✅ Upload OMR sheet images (PNG, JPEG)
- ✅ Automatic image preprocessing and alignment
- ✅ Bubble detection with confidence scores
- ✅ Answer key evaluation and scoring
- ✅ Detailed results with per-question feedback
- ✅ Summary statistics (total marks, correct/wrong counts)

## Project Structure

```
omr_webapp/
├── backend/
│   ├── main.py
│   ├── template.json
│   └── utils/
│       ├── preprocess.py
│       ├── detect.py
│       ├── json_output.py
│       └── evaluation.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── samples/
│   └── sample_omr.jpg
├── requirements.txt
└── README.md
```

## Quick Start (Local)

```bash
cd omr_webapp
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the provided scripts:
- Windows: `run.bat`
- PowerShell: `run.ps1`

Open the frontend by navigating to `http://localhost:8000` in your browser (the frontend is served by FastAPI).

## Configuration

Edit `backend/template.json` to configure:
- Number of questions
- Answer options (A, B, C, D, etc.)
- Grid layout (bubble positions)
- **Answer key** for evaluation

Example `template.json`:
```json
{
  "questions": 10,
  "options": ["A", "B", "C", "D"],
  "answer_key": {
    "1": "B",
    "2": "D",
    "3": "A"
  },
  "grid": {
    "start_x": 0.1,
    "start_y": 0.2,
    "row_gap": 0.08,
    "col_gap": 0.15,
    "bubble_width": 0.05,
    "bubble_height": 0.05
  }
}
```

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
  },
  "evaluation": {
    "1": {
      "student_answer": "B",
      "correct_answer": "B",
      "is_correct": true,
      "marks": 1
    },
    "2": {
      "student_answer": "A",
      "correct_answer": "D",
      "is_correct": false,
      "marks": 0
    },
    "summary": {
      "total_questions": 2,
      "correct": 1,
      "wrong": 1,
      "total_marks": 1
    }
  }
}
```

`GET /health`

- Returns `{"status": "ok"}`

## Deployment

### Render.com / Railway.app

1. Push this repo to GitHub.
2. Create a new **Web Service**.
3. Set:
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Build Command**: `pip install -r requirements.txt`
4. Set the service port to match the platform's assigned port.

### AWS EC2 (Ubuntu)

```bash
sudo apt update && sudo apt install -y python3-venv
git clone <your repo>
cd omr_webapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Use Nginx or an ALB to expose port 8000 publicly.

## Logging

The backend writes logs to `backend/logs/app.log` and console. Rotate/ship as needed.

## Sample Asset

`samples/sample_omr.jpg` is a placeholder. Replace it with a real OMR sheet image to test detection.
