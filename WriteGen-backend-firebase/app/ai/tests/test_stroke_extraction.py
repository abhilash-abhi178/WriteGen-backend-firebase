# app/ai/tests/test_stroke_extraction.py
import pytest
import asyncio
from app.ai.services.stroke_engine import StrokeEngine
from PIL import Image, ImageDraw
import os

@pytest.mark.asyncio
async def test_extract_strokes(tmp_path):
    # create a simple black-on-white image with a line
    p = tmp_path / "line.png"
    img = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.line((10,50,190,50), fill="black", width=5)
    img.save(p)

    engine = StrokeEngine(tmp_dir=str(tmp_path))
    proc = await engine.preprocess(str(p))
    strokes = await engine.extract_strokes(proc)
    # we expect at least one stroke in the result
    assert isinstance(strokes, list)
    assert len(strokes) >= 1
