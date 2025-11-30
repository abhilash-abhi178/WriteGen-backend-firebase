# app/services/ocr_service.py
import pytesseract
from PIL import Image
from typing import List

class OCRService:
    def __init__(self):
        pass

    async def extract_text(self, image_path: str) -> str:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text

    async def extract_lines(self, image_path: str) -> List[str]:
        img = Image.open(image_path)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        lines = []
        current_line = []
        last_block_num = None
        for i, text in enumerate(data['text']):
            if not text.strip():
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
