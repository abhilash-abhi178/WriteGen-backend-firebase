# app/ai/utils/svg_utils.py
from typing import List, Dict

def svg_path_to_plain(path_str: str) -> str:
    # placeholder helper: currently returns input
    return path_str

def wrap_paths_into_svg(paths: List[Dict], width: int = 2480, height: int = 3508) -> str:
    """
    Build a minimal SVG string from paths (each dict with 'd', 'stroke', 'stroke_width', 'transform')
    """
    header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
    body = []
    for p in paths:
        d = p.get("d") or p.get("path") or ""
        stroke = p.get("stroke", "#000")
        sw = p.get("stroke_width", 2)
        transform = p.get("transform", "")
        tattr = f' transform="{transform}"' if transform else ""
        body.append(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="none"{tattr} />')
    footer = "</svg>"
    return "\n".join([header] + body + [footer])
