# stroke extraction using potrace + OpenCV
import os
from typing import List, Dict, Any
from PIL import Image
import numpy as np
import cv2
import potrace

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
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        # adaptive threshold
        bin_img = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
        out_path = os.path.join(self.tmp_dir, os.path.basename(image_path) + "_proc.png")
        cv2.imwrite(out_path, bin_img)
        return out_path

    async def extract_strokes(self, bin_image_path: str) -> List[Dict[str, Any]]:
        im = Image.open(bin_image_path).convert("1")
        arr = np.array(im, dtype=np.uint8)
        # potrace expects 1 for black pixels; Pillow's '1' mode uses 0/255; convert to boolean
        bitmap = potrace.Bitmap(arr)
        path_iter = bitmap.trace()
        strokes = []
        for curve in path_iter:
            svg_path = self._curve_to_svg(curve)
            strokes.append({
                "path": svg_path,
                "bbox": getattr(curve, "bbox", None),
                "closed": getattr(curve, "is_closed", False),
                "segments": len(curve.segments) if hasattr(curve, "segments") else None
            })
        return strokes

    def _curve_to_svg(self, curve) -> str:
        # Convert potrace curve object to basic SVG path (commands)
        parts = []
        # start_point may be tuple or object
        sp = getattr(curve, "start_point", None)
        if sp is None:
            # fallback
            return ""
        parts.append(f"M{sp[0]},{sp[1]}")
        for seg in curve:
            # potrace curve iteration yields segments; adapt pattern
            try:
                if seg.is_corner:
                    # two points: c, end
                    c = seg.c
                    end = seg.end_point
                    parts.append(f"L{c[0]},{c[1]} L{end[0]},{end[1]}")
                else:
                    c1 = seg.c1
                    c2 = seg.c2
                    end = seg.end_point
                    parts.append(f"C{c1[0]},{c1[1]} {c2[0]},{c2[1]} {end[0]},{end[1]}")
            except Exception:
                # Defensive: skip malformed segments
                continue
        if getattr(curve, "is_closed", False):
            parts.append("Z")
        return " ".join(parts)
