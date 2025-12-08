# app/ai/tests/test_style_training.py
import pytest
import asyncio
from app.ai.services.style_service import StyleService
from app.ai.services.stroke_engine import StrokeEngine
from PIL import Image, ImageDraw
import os
import json

@pytest.mark.asyncio
async def test_build_style_profile(tmp_path):
    # Prepare fake processed images and transcripts
    p1 = tmp_path / "s1_proc.png"
    img = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.text((10,10), "abc", fill="black")
    img.save(p1)

    sample_docs = [{"processed_path": str(p1), "transcript": "abc", "user_id": "u1"}]
    engine = StrokeEngine(tmp_dir=str(tmp_path))
    service = StyleService(engine)
    profile = await service.build_style_profile(sample_docs)
    assert "character_database" in profile
    # 'a' or 'b' or 'c' may be present depending on potrace output but structure should be dict
    assert isinstance(profile["character_database"], dict)
