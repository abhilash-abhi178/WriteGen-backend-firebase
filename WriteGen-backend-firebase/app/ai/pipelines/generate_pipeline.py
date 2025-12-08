# app/ai/pipelines/generate_pipeline.py
"""
Orchestrates generation:
1. Load style (from DB or object provided)
2. Ask GenerationService to create document
3. Return resulting path or raise
"""
from typing import Dict, Any
from app.ai.services import StyleService, GenerationService, StrokeEngine

async def generate_pipeline(style_profile: Dict[str, Any], text: str, settings: Dict[str, Any]) -> str:
    engine = StrokeEngine()
    style_service = StyleService(engine)
    gen_service = GenerationService(style_service)
    output_path = await gen_service.generate_document(style_profile, text, settings)
    return output_path
