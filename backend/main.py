import json
import logging
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from utils import detect, preprocess, json_output, evaluation

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("omr-backend")

app = FastAPI(title="OMR Scanner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATE_PATH = BASE_DIR / "template.json"


def load_template() -> dict:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError("template.json missing.")
    with TEMPLATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


template_cache = load_template()

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def _validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing.")
    if file.content_type not in {"image/png", "image/jpeg", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Only PNG or JPEG images are supported.")


@app.post("/scan")
async def scan_sheet(file: UploadFile = File(...)) -> JSONResponse:
    _validate_file(file)
    suffix = Path(file.filename).suffix or ".png"

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_path = Path(temp_file.name)
    try:
        logger.info("Receiving file: %s", file.filename)
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()

        image = preprocess.load_image(str(temp_path))
        frames = preprocess.preprocess_for_detection(image)
        answers = detect.detect_answers(frames, template_cache)

        answer_key = template_cache.get("answer_key", {})
        student_choices = {q: data["choice"] for q, data in answers.items()}
        evaluation_result = evaluation.evaluate(student_choices, answer_key)
        json_output.save_result(evaluation_result)
        payload = json_output.build_response(answers, evaluation_result)

        summary = evaluation_result.get("summary", {})
        logger.info(
            "Detection completed. Questions: %d | Score: %s/%s",
            len(answers),
            summary.get("total_marks"),
            summary.get("total_questions"),
        )
        return JSONResponse(content=payload)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to process OMR sheet: %s", exc)
        raise HTTPException(status_code=500, detail="Processing failed. Please try again.") from exc
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

