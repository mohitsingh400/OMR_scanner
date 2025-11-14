from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _get_region(bounds: Tuple[int, int, int, int], image: np.ndarray) -> np.ndarray:
    x1, y1, x2, y2 = bounds
    return image[y1:y2, x1:x2]


def _calc_bounds(
    idx_question: int,
    idx_option: int,
    width: int,
    height: int,
    grid_cfg: Dict[str, float],
) -> Tuple[int, int, int, int]:
    start_x = grid_cfg["start_x"] + idx_option * grid_cfg["col_gap"]
    start_y = grid_cfg["start_y"] + idx_question * grid_cfg["row_gap"]
    bubble_w = grid_cfg["bubble_width"]
    bubble_h = grid_cfg["bubble_height"]

    x1 = int(width * start_x)
    y1 = int(height * start_y)
    x2 = int(width * (start_x + bubble_w))
    y2 = int(height * (start_y + bubble_h))

    x1 = max(0, min(width - 1, x1))
    x2 = max(x1 + 1, min(width, x2))
    y1 = max(0, min(height - 1, y1))
    y2 = max(y1 + 1, min(height, y2))
    return x1, y1, x2, y2


def detect_answers(frames: Dict[str, np.ndarray], template: Dict) -> Dict[str, Dict[str, float]]:
    """Infer the selected bubbles using a simple grid template."""
    binary = frames["binary"]
    deskewed = frames["deskewed"]
    height, width = binary.shape

    questions = template["questions"]
    options: List[str] = template["options"]
    grid_cfg = template["grid"]

    answers: Dict[str, Dict[str, float]] = {}
    for q in range(questions):
        per_option_scores = []
        for opt_idx, label in enumerate(options):
            bounds = _calc_bounds(q, opt_idx, width, height, grid_cfg)
            region = _get_region(bounds, binary)
            if region.size == 0:
                per_option_scores.append((label, 0.0))
                continue

            filled_pixels = float(np.count_nonzero(region))
            ratio = filled_pixels / region.size

            # Also check the raw grayscale to reduce noise.
            gray_region = _get_region(bounds, frames["gray"])
            darkness = 1.0 - (float(np.mean(gray_region)) / 255.0)

            score = (ratio * 0.6) + (darkness * 0.4)
            per_option_scores.append((label, score))

        per_option_scores.sort(key=lambda item: item[1], reverse=True)
        best_label, best_score = per_option_scores[0]
        runner_up = per_option_scores[1][1] if len(per_option_scores) > 1 else 0.0
        confidence_gap = best_score - runner_up
        confidence = _clamp(best_score * 0.8 + confidence_gap * 0.2)

        answers[str(q + 1)] = {
            "choice": best_label,
            "confidence": round(confidence, 3),
        }

    return answers

