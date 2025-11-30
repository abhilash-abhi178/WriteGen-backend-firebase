# app/services/ocr_service.py
import pytesseract
import cv2
from PIL import Image
from typing import List


class OCRService:
    def __init__(self):
        pass

    async def extract_text(self, image_path: str) -> str:
        # Preprocess with OpenCV for more consistent OCR
        img = cv2.imread(image_path)
        if img is None:
            return ""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        pil_img = Image.fromarray(thresh)
        text = pytesseract.image_to_string(pil_img, lang='eng')
        return text

    async def extract_lines(self, image_path: str) -> List[str]:
        img = cv2.imread(image_path)
        if img is None:
            return []
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        pil_img = Image.fromarray(thresh)
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
        lines = []
        current_line = []
        last_block_num = None
        for i, text in enumerate(data.get('text', [])):
            if not text or not text.strip():
                continue
            block_num = data['block_num'][i]
            if last_block_num is None:
                last_block_num = block_num
            if block_num != last_block_num:
                lines.append(" ".join(current_line))
                current_line = []
                last_block_num = block_num
            current_line.append(text)
        if current_line:
            lines.append(" ".join(current_line))
        return lines
