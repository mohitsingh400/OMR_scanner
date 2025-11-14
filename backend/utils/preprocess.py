import cv2
import numpy as np
from typing import Tuple, Dict


def load_image(path: str) -> np.ndarray:
    """Read the image in color and raise if not found."""
    image = cv2.imread(path)
    if image is None:
        raise ValueError("Unable to read the uploaded image.")
    return image


def resize_image(image: np.ndarray, max_width: int = 1200) -> np.ndarray:
    """Scale the image down while keeping the aspect ratio."""
    h, w = image.shape[:2]
    if w <= max_width:
        return image
    scale = max_width / float(w)
    new_size = (int(w * scale), int(h * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def deskew_image(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """Attempt to auto-align a slightly rotated sheet."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = cv2.HoughLines(edges, 1, np.pi / 180.0, 150)
    angle = 0.0
    if lines is not None:
        angles = []
        for line in lines[:20]:
            rho, theta = line[0]
            deg = (theta * 180.0 / np.pi) - 90
            if -45 < deg < 45:
                angles.append(deg)
        if angles:
            angle = float(np.median(angles))

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return rotated, angle


def preprocess_for_detection(image: np.ndarray) -> Dict[str, np.ndarray]:
    """Return intermediate grayscale/binary images for downstream detection."""
    resized = resize_image(image)
    deskewed, _ = deskew_image(resized)
    gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25,
        10,
    )

    return {
        "original": image,
        "resized": resized,
        "deskewed": deskewed,
        "gray": gray,
        "binary": binary,
    }

