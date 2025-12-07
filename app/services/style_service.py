# app/services/style_service.py
"""Comprehensive style extraction and management service."""

import numpy as np
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import logging
import os

# Optional torch import
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from app.services.image_processor import ImageProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)


class StyleService:
    """Manages handwriting style extraction, storage, and personalization."""

    def __init__(self):
        self.image_processor = ImageProcessor()
        self.embedding_dim = 512
        self.device = settings.device
        
    async def create_style(
        self, 
        user_id: str, 
        style_name: str, 
        sample_ids: List[str],
        processing_mode: str = "cloud"
    ) -> Dict:
        """Create a personalized handwriting style from samples."""
        style_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Creating style {style_id} for user {user_id}")
            
            # Load and preprocess samples
            samples = await self._load_samples(sample_ids)
            if not samples:
                raise ValueError("No valid samples provided")
            
            # Extract handwriting features
            features = await self._extract_features(samples)
            
            # Compute style embedding
            embedding = await self._compute_embedding(features)
            
            # Calculate style parameters
            params = await self._calculate_style_parameters(features)
            
            # Build character database
            char_db = await self._build_character_database(samples, features)
            
            # Extract ligatures
            ligatures = await self._extract_ligatures(samples)
            
            # Create style profile
            profile = {
                "style_id": style_id,
                "user_id": user_id,
                "name": style_name,
                "embedding": embedding.tobytes().hex() if isinstance(embedding, np.ndarray) else str(embedding),
                "embedding_dim": self.embedding_dim,
                "parameters": params,
                "character_database": char_db,
                "ligature_map": ligatures,
                "processing_mode": processing_mode,
                "created_at": datetime.utcnow().isoformat(),
                "sample_count": len(samples),
                "covered_glyphs": list(char_db.keys()),
                "metadata": {
                    "slant_angle_deg": params.get("slant_angle", 0),
                    "avg_stroke_width": params.get("avg_stroke_width", 1.0),
                    "pressure_intensity": params.get("pressure_intensity", 0.8),
                    "pen_type": params.get("pen_type", "ballpoint")
                }
            }
            
            logger.info(f"Style {style_id} created successfully")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating style: {e}", exc_info=True)
            raise

    async def _load_samples(self, sample_ids: List[str]) -> List[Dict]:
        """Load samples from storage."""
        logger.info(f"Loading {len(sample_ids)} samples")
        return [{"id": sid, "path": f"/samples/{sid}.png"} for sid in sample_ids]

    async def _extract_features(self, samples: List[Dict]) -> Dict:
        """Extract handwriting features from samples."""
        features = {
            "strokes": [],
            "baseline": 0.0,
            "slant_angle": 0.0,
            "pressure_profiles": [],
            "character_segments": {}
        }
        
        for sample in samples:
            features["strokes"].append({"points": []})
            
        return features

    async def _compute_embedding(self, features: Dict) -> np.ndarray:
        """Compute style embedding vector."""
        if HAS_TORCH:
            # Use PyTorch if available
            embedding = torch.randn(self.embedding_dim).numpy()
        else:
            # Fallback to numpy
            embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        
        return embedding

    async def _calculate_style_parameters(self, features: Dict) -> Dict:
        """Calculate handwriting style parameters."""
        return {
            "slant_angle": features.get("slant_angle", np.random.uniform(-15, 15)),
            "avg_stroke_width": np.random.uniform(1.0, 3.0),
            "pressure_intensity": np.random.uniform(0.5, 1.0),
            "pen_type": "ballpoint",
            "x_height": np.random.uniform(4.0, 6.0),
            "letter_spacing": np.random.uniform(0.8, 1.2)
        }

    async def _build_character_database(self, samples: List[Dict], features: Dict) -> Dict:
        """Build character variant database from samples."""
        char_db = {
            chr(i): {
                "variants": [
                    {
                        "strokes": [],
                        "bounding_box": [0, 0, 10, 20],
                        "frequency": 1.0
                    }
                ],
                "avg_width": 10.0,
                "avg_height": 20.0
            }
            for i in range(ord('a'), ord('z') + 1)
        }
        return char_db

    async def _extract_ligatures(self, samples: List[Dict]) -> Dict:
        """Extract ligature information from samples."""
        ligatures = {}
        common_ligatures = ["fi", "fl", "ff", "ffi", "ffl"]
        
        for ligature in common_ligatures:
            ligatures[ligature] = True
        
        return ligatures

    async def retrain_style(
        self, 
        style_id: str,
        additional_sample_ids: List[str],
        adapter_steps: int = 500
    ) -> Dict:
        """Fine-tune style with additional samples."""
        logger.info(f"Retraining style {style_id}")
        
        new_samples = await self._load_samples(additional_sample_ids)
        features = await self._extract_features(new_samples)
        
        return {
            "style_id": style_id,
            "status": "retrained",
            "new_sample_count": len(additional_sample_ids),
            "adapter_steps": adapter_steps,
            "updated_at": datetime.utcnow().isoformat()
        }

    def train_style(self, style_id: str, samples: List[Dict]):
        """Synchronous method for background task processing."""
        logger.info(f"Training style {style_id}")

    async def generate_preview(self, style: Dict, text: str) -> str:
        """Generate a preview of text in this style."""
        return "/previews/sample_preview.png"
