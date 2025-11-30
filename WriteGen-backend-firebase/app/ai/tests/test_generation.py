# app/ai/tests/test_generation.py
import pytest
import asyncio
from app.ai.services.generation_service import GenerationService
from app.ai.services.style_service import StyleService
from app.ai.services.stroke_engine import StrokeEngine
from PIL import Image, ImageDraw
import os

@pytest.mark.asyncio
async def test_generate_document(tmp_path):
    # Prepare minimal fake style_profile
    style_profile = {
        "character_database": {
            "H": {"variants":[{"path":"M0,0 L10,0", "bbox":[0,0,10,10]}], "avg_width": 10},
            "i": {"variants":[{"path":"M0,0 L2,0", "bbox":[0,0,2,8]}], "avg_width": 2},
            " ": {}
        }
    }
    engine = StrokeEngine(tmp_dir=str(tmp_path))
    style_service = StyleService(engine)
    gen = GenerationService(style_service, outputs_dir=str(tmp_path))
    out = await gen.generate_document(style_profile, "Hi Hi\nHi", {"ink_color":"#123456", "thickness":1})
    assert out.endswith(".svg")
    assert os.path.exists(out)
