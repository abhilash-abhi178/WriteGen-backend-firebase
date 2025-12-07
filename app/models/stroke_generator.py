"""Placeholder stroke generator model wrapper.

This stub keeps the codebase runnable without shipping heavy model weights.
Replace with actual model loading/inference when models are available.
"""
from typing import Any, Dict, List, Optional

try:
    import torch
    HAS_TORCH = True
except ImportError:  # Torch is optional for lightweight environments
    HAS_TORCH = False


class StrokeGenerator:
    """Mock stroke generator that returns simple stroke sequences."""

    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model: Optional[Any] = None
        if HAS_TORCH and model_path:
            try:
                self.model = torch.jit.load(model_path, map_location=device)
                self.model.eval()
            except Exception:
                # Keep stub behavior if load fails
                self.model = None

    def generate(self, tokens: List[int], style_embedding) -> List[Dict]:
        """Generate stroke dictionaries for given tokens.

        This stub emits deterministic straight-line strokes per character; replace
        with real model inference for production.
        """
        strokes: List[Dict] = []
        for tok in tokens:
            if tok < 0:
                strokes.append({"type": "special", "token": tok, "points": []})
                continue
            points = [
                {"x": float(i * 2), "y": float(i * 3), "pressure": 0.8}
                for i in range(6)
            ]
            strokes.append({"type": "glyph", "character": chr(tok), "points": points})
        return strokes
