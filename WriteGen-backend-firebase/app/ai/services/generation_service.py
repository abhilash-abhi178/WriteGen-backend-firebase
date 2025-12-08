# generate handwriting by cloning strokes and composing SVG pages
import os
import random
from typing import List, Dict, Any
from datetime import datetime
import svgwrite
from app.ai.services.style_service import StyleService

class GenerationService:
    def __init__(self, style_service: StyleService, outputs_dir: str = "outputs"):
        self.style_service = style_service
        self.outputs_dir = outputs_dir
        os.makedirs(outputs_dir, exist_ok=True)
        self.page_w = 2480
        self.page_h = 3508

    async def generate_document(self, style_profile: Dict[str, Any], text: str, settings: Dict[str, Any]) -> str:
        """
        Returns path to saved SVG output
        """
        # Convert text to stroke sequence
        char_db = style_profile.get("character_database", {})
        x, y = 100, 150  # margins
        line_height = settings.get("line_height", 80)
        strokes_to_render = []
        for ch in text:
            if ch == "\n":
                x = 100
                y += line_height
                continue
            if ch.isspace():
                x += settings.get("space", 40)
                continue
            variants = char_db.get(ch)
            if not variants:
                x += settings.get("space", 40)
                continue
            selected = random.choice(variants["variants"])
            # note: path is assumed to be absolute path coordinates - will translate
            strokes_to_render.append({"path": selected["path"], "x": x, "y": y, "ch": ch})
            x += variants.get("avg_width", 40) + settings.get("letter_spacing", 6)
            if x > self.page_w - 100:
                x = 100
                y += line_height

        # render to svg
        ts = int(datetime.utcnow().timestamp())
        out_path = os.path.join(self.outputs_dir, f"generated_{ts}.svg")
        dwg = svgwrite.Drawing(out_path, size=(f"{self.page_w}px", f"{self.page_h}px"))
        page_group = dwg.g(id="page_0")
        for s in strokes_to_render:
            path = dwg.path(d=s["path"], stroke=settings.get("ink_color", "#000"), stroke_width=settings.get("thickness", 2),
                            fill="none", stroke_linecap="round", stroke_linejoin="round")
            path.translate(s["x"], s["y"])
            page_group.add(path)
        dwg.add(page_group)
        dwg.save()
        return out_path
