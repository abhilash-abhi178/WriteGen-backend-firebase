# app/ai/pipelines/train_style_pipeline.py
"""
High-level orchestration to create a style profile from sample docs.
This is lightweight and intended to be launched as a background task.
"""
from typing import List, Dict, Any
from app.ai.services import StrokeEngine, StyleService
import asyncio

async def train_style_pipeline(sample_docs: List[Dict[str, Any]]):
    engine = StrokeEngine()
    style_service = StyleService(engine)
    # Build profile (IO bound)
    profile = await style_service.build_style_profile(sample_docs)
    # return profile to caller (DB saving is caller's responsibility)
    return profile
