# utilities to convert SVG to PDF/PNG if needed (using cairosvg or reportlab)
import os
from typing import Optional
import cairosvg

class RendererService:
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = outputs_dir

    async def svg_to_pdf(self, svg_path: str, pdf_path: Optional[str] = None) -> str:
        out = pdf_path or svg_path.replace(".svg", ".pdf")
        cairosvg.svg2pdf(url=svg_path, write_to=out)
        return out

    async def svg_to_png(self, svg_path: str, png_path: Optional[str] = None, dpi: int = 300) -> str:
        out = png_path or svg_path.replace(".svg", ".png")
        cairosvg.svg2png(url=svg_path, write_to=out, dpi=dpi)
        return out
