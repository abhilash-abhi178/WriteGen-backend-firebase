# app/services/image_processor.py
import cv2
import numpy as np
from PIL import Image
import potrace
from typing import List, Dict
import os
from app.core.config import settings

class ImageProcessor:
    def __init__(self):
        self.target_dpi = 300
        self.tmp_dir = settings.temp_dir
        os.makedirs(self.tmp_dir, exist_ok=True)

    async def process_image(self, image_path: str) -> str:
        img = cv2.imread(image_path)
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
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
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
        img = Image.open(image_path).convert('1')
        img_array = np.array(img)
        bmp = potrace.Bitmap(img_array)
        path = bmp.trace()
        strokes = []
        for curve in path:
            stroke_data = {
                "path": self._curve_to_svg_path(curve),
                "bbox": getattr(curve, "bbox", None),
                "length": len(curve.segments)
            }
            strokes.append(stroke_data)
        return strokes

    def _curve_to_svg_path(self, curve) -> str:
        path_parts = []
        start_point = curve.start_point
        path_parts.append(f"M{start_point[0]},{start_point[1]}")
        for segment in curve.segments:
            if segment.is_corner:
                c = segment.c
                end_point = segment.end_point
                path_parts.append(f"L{c[0]},{c[1]} L{end_point[0]},{end_point[1]}")
            else:
                c1 = segment.c1
                c2 = segment.c2
                end_point = segment.end_point
                path_parts.append(f"C{c1[0]},{c1[1]} {c2[0]},{c2[1]} {end_point[0]},{end_point[1]}")
        if curve.is_closed:
            path_parts.append("Z")
        return " ".join(path_parts)
