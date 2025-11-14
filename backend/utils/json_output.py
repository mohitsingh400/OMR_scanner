from pathlib import Path
import json
from typing import Dict, Any

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "result.json"


def build_response(answers: Dict[str, Dict[str, float]], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "success",
        "answers": answers,
        "evaluation": evaluation,
    }


def save_result(evaluation: Dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2)

