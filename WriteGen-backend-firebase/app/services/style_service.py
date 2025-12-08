# app/services/style_service.py
import numpy as np
from collections import defaultdict
from app.core.firebase import db
from typing import List, Dict
from datetime import datetime
from app.services.image_processor import ImageProcessor

class StyleService:
    def __init__(self):
        self.image_processor = ImageProcessor()

    async def train_style(self, style_id: str, samples: List[Dict]):
        try:
            db.collection("styles").document(style_id).update({"status": "training", "progress": 0.1})
        except Exception:
            pass

        all_strokes = []
        for s in samples:
            strokes = s.get("strokes", [])
            transcript = s.get("transcript", "")
            all_strokes.extend(strokes)

        char_db = await self._build_character_database(samples)
        style_params = await self._calculate_style_parameters(samples)
        ligatures = await self._extract_ligatures(samples)

        profile = {
            "character_database": char_db,
            "style_parameters": style_params,
            "ligature_map": ligatures,
            "metadata": {"total_characters": len(char_db), "total_strokes": len(all_strokes), "samples_used": len(samples)}
        }

        db.collection("styles").document(style_id).update({
            "status": "trained",
            "progress": 1.0,
            "profile": profile,
            "trained_at": datetime.utcnow().isoformat()
        })

    async def _build_character_database(self, samples: List[Dict]) -> Dict:
        char_db = defaultdict(lambda: {"variants": [], "avg_width": 0, "avg_height": 0})
        for sample in samples:
            transcript = sample.get("transcript", "")
            strokes = sample.get("strokes", [])
            chars_per_stroke = len(transcript) / max(len(strokes), 1)
            for i, ch in enumerate(transcript):
                if ch.isspace():
                    continue
                stroke_idx = int(i / chars_per_stroke)
                if stroke_idx < len(strokes):
                    stroke = strokes[stroke_idx]
                    variant = {"path": stroke.get("path"), "bbox": stroke.get("bbox"), "frequency": 1}
                    char_db[ch]["variants"].append(variant)
        for ch, data in char_db.items():
            if data["variants"]:
                bboxes = [v["bbox"] for v in data["variants"] if v.get("bbox")]
                widths = [bbox[2] - bbox[0] for bbox in bboxes] if bboxes else [10]
                heights = [bbox[3] - bbox[1] for bbox in bboxes] if bboxes else [10]
                data["avg_width"] = float(np.mean(widths))
                data["avg_height"] = float(np.mean(heights))
                total = len(data["variants"])
                for variant in data["variants"]:
                    variant["frequency"] = 1.0 / total
        return dict(char_db)

    async def _calculate_style_parameters(self, samples: List[Dict]) -> Dict:
        all_metadata = [s.get("metadata", {}) for s in samples]
        params = {
            "slant_angle": float(np.mean([m.get("slant_angle", 0) for m in all_metadata])) if all_metadata else 0.0,
            "avg_spacing": float(np.mean([m.get("avg_spacing", 10) for m in all_metadata])) if all_metadata else 10.0,
            "baseline_drift": float(np.mean([m.get("baseline_drift", 0) for m in all_metadata])) if all_metadata else 0.0,
            "stroke_thickness": float(np.mean([m.get("avg_stroke_thickness", 2) for m in all_metadata])) if all_metadata else 2.0,
            "natural_variation": 0.05
        }
        return params

    async def _extract_ligatures(self, samples: List[Dict]) -> Dict:
        ligatures = {}
        common_pairs = ["th", "he", "in", "er", "an", "re", "on", "at", "en", "nd"]
        for sample in samples:
            transcript = sample.get("transcript", "")
            for pair in common_pairs:
                if pair in transcript.lower():
                    ligatures[pair] = {"connected": True}
        return ligatures

    async def generate_preview(self, style: Dict, text: str) -> str:
        return "/previews/sample_preview.png"
