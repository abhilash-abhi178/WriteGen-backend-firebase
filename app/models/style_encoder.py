"""Placeholder style encoder wrapper.

Produces a fixed-size embedding so downstream services can run without real models.
Replace with actual encoder weights and preprocessing when available.
"""
import numpy as np
from typing import Any, List, Optional

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class StyleEncoder:
    """Mock style encoder returning deterministic embeddings."""

    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        self.model: Optional[Any] = None
        if HAS_TORCH and model_path:
            try:
                self.model = torch.jit.load(model_path, map_location=device)
                self.model.eval()
            except Exception:
                self.model = None

    def encode(self, images: List[str]) -> np.ndarray:
        """Return a 512-d embedding; real impl should use vision/stroke features."""
        if not images:
            return np.zeros(512, dtype=np.float32)
        seed = sum(len(p) for p in images) % 997
        rng = np.random.default_rng(seed)
        return rng.random(512, dtype=np.float32)
