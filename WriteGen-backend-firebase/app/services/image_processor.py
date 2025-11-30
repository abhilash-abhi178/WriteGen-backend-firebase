# app/services/image_processor.py
import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Tuple
import os
from app.core.config import settings


class ImageProcessor:
    def __init__(self):
        self.target_dpi = 300
        self.tmp_dir = settings.temp_dir
        os.makedirs(self.tmp_dir, exist_ok=True)

    async def process_image(self, image_path: str) -> str:
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        deskewed = self._deskew_image(gray)
        cropped = self._auto_crop(deskewed)
        enhanced = self._enhance_contrast(cropped)
        binary = self._binarize(enhanced)

        processed_path = image_path.rsplit(".", 1)[0] + "_processed.png"
        cv2.imwrite(processed_path, binary)
        return processed_path

    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)
        if lines is None:
            return image
        angles = []
        for line in lines:
            rho, theta = line[0]
            angle = (theta * 180 / np.pi) - 90
            if -45 < angle < 45:
                angles.append(angle)
        if not angles:
            return image
        median_angle = np.median(angles)
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def _auto_crop(self, image: np.ndarray) -> np.ndarray:
        _, thresh = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image
        x_min, y_min = image.shape[1], image.shape[0]
        x_max, y_max = 0, 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)
        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(image.shape[1], x_max + padding)
        y_max = min(image.shape[0], y_max + padding)
        cropped = image[y_min:y_max, x_min:x_max]
        return cropped

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced

    def _binarize(self, image: np.ndarray) -> np.ndarray:
        binary = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        return binary

    async def extract_strokes(self, image_path: str) -> List[Dict]:
        # Use OpenCV contours as stroke approximations (raster -> simplified paths)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return []
        # Ensure binary image
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        strokes: List[Dict] = []
        for cnt in contours:
            if cnt is None or len(cnt) == 0:
                continue
            # approximate contour to reduce points
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            points = [tuple(pt[0]) for pt in approx]
            # build simple SVG-like path (M + L commands)
            if not points:
                continue
            path_str = f"M{points[0][0]},{points[0][1]}"
            for (x, y) in points[1:]:
                path_str += f" L{x},{y}"
            if cv2.contourArea(cnt) > 0 and cv2.isContourConvex(approx):
                path_str += " Z"
            x, y, w, h = cv2.boundingRect(cnt)
            stroke_data = {
                "path": path_str,
                "bbox": (int(x), int(y), int(x + w), int(y + h)),
                "length": len(points)
            }
            strokes.append(stroke_data)
        return strokes

    def _curve_to_svg_path(self, curve) -> str:
        # This helper belonged to potrace-based implementation and is no longer used.
        return ""
