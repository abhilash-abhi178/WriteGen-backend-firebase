# style creation (character stroke DB + simple stats)
import json
import numpy as np
from typing import List, Dict, Any
from app.ai.services.stroke_engine import StrokeEngine

class StyleService:
    def __init__(self, stroke_engine: StrokeEngine):
        self.stroke_engine = stroke_engine

    async def build_style_profile(self, sample_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        sample_docs: list of dicts with keys { 'processed_path', 'transcript', 'user_id' }
        Return: style_profile dict (character -> variants)
        """
        char_db = {}
        for sample in sample_docs:
            processed = sample.get("processed_path")
            transcript = sample.get("transcript", "")
            strokes = await self.stroke_engine.extract_strokes(processed)
            # naive mapping: equal partitioning (improve later with alignment)
            chars = [c for c in transcript]
            if not strokes:
                continue
            per = max(1, len(strokes) // max(1, len(chars)))
            for i, ch in enumerate(chars):
                if ch.isspace(): continue
                idx = min(len(strokes)-1, i*per)
                entry = {"path": strokes[idx]["path"], "bbox": strokes[idx]["bbox"]}
                char_db.setdefault(ch, {"variants": []})["variants"].append(entry)
        # compute averages
        for ch, data in char_db.items():
            variants = data["variants"]
            data["avg_width"] = float(np.mean([ (v["bbox"][2]-v["bbox"][0]) if v["bbox"] else 0 for v in variants ])) if variants else 0
            data["avg_height"] = float(np.mean([ (v["bbox"][3]-v["bbox"][1]) if v["bbox"] else 0 for v in variants ])) if variants else 0
        profile = {"character_database": char_db, "meta": {"num_chars": len(char_db)}}
        return profile
