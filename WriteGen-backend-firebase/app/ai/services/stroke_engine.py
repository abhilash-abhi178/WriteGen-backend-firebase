# stroke extraction using OpenCV contours (no potrace)
import os
from typing import List, Dict, Any, Tuple
from PIL import Image
import numpy as np
import cv2


class StrokeEngine:
    def __init__(self, tmp_dir: str = "/tmp"):
        self.tmp_dir = tmp_dir
        os.makedirs(self.tmp_dir, exist_ok=True)

    async def preprocess(self, image_path: str) -> str:
        # deskew, enhance, binarize and write processed path
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # simple denoise + CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        # adaptive threshold
        bin_img = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
        out_path = os.path.join(self.tmp_dir, os.path.basename(image_path) + "_proc.png")
        cv2.imwrite(out_path, bin_img)
        return out_path

    async def extract_strokes(self, bin_image_path: str) -> List[Dict[str, Any]]:
        # Use OpenCV contours to approximate strokes from a binarized image
        img = cv2.imread(bin_image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return []
        # Ensure binary (invert so strokes are white on black for findContours if needed)
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Invert so contours correspond to ink regions
        thresh_inv = cv2.bitwise_not(thresh)
        contours, _ = cv2.findContours(thresh_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        strokes: List[Dict[str, Any]] = []
        for cnt in contours:
            if cnt is None or len(cnt) == 0:
                continue
            # approximate contour to reduce points
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            points = [tuple(pt[0]) for pt in approx]
            if not points:
                continue
            # build simple path (M + L commands)
            path_str = f"M{points[0][0]},{points[0][1]}"
            for (x, y) in points[1:]:
                path_str += f" L{x},{y}"
            x, y, w, h = cv2.boundingRect(cnt)
            stroke = {
                "path": path_str,
                "bbox": (int(x), int(y), int(x + w), int(y + h)),
                "closed": bool(cv2.isContourConvex(approx)),
                "segments": len(points)
            }
            strokes.append(stroke)
        return strokes
