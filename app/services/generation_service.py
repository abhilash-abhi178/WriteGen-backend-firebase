# app/services/generation_service.py
"""Text-to-handwriting generation service."""

import os
import uuid
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Optional torch import
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class GenerationService:
    """Core text-to-handwriting generation engine."""

    def __init__(self):
        self.device = settings.device
        self.max_sequence_length = 1024
        
    async def generate_handwriting(
        self,
        style_embedding: np.ndarray,
        text: str,
        pen_settings: Optional[Dict] = None,
        page_settings: Optional[Dict] = None,
        mode: str = "fast"
    ) -> Dict:
        """Generate handwriting from text using a style.
        
        Args:
            style_embedding: 512-d style vector
            text: Text to generate
            pen_settings: Pen customization
            page_settings: Page layout settings
            mode: "fast" (autoregressive) or "quality" (diffusion)
            
        Returns:
            Generated strokes and page layout
        """
        logger.info(f"Generating handwriting: {len(text)} chars, mode={mode}")
        
        try:
            # Tokenize text
            tokens = await self._tokenize_text(text)
            
            # Generate strokes based on mode
            if mode == "quality":
                strokes = await self._generate_strokes_diffusion(tokens, style_embedding)
            else:
                strokes = await self._generate_strokes_autoregressive(tokens, style_embedding)
            
            # Apply layout
            layout_strokes = await self._apply_layout_and_style(
                strokes,
                style_embedding,
                pen_settings or {},
                page_settings or {}
            )
            
            # Paginate
            pages = await self._paginate_strokes(layout_strokes)
            
            result = {
                "text": text,
                "stroke_count": len(strokes),
                "page_count": len(pages),
                "pages": pages,
                "mode": mode,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated {len(pages)} pages")
            return result
            
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            raise

    async def _tokenize_text(self, text: str) -> List[int]:
        """Convert text to tokens."""
        tokens = []
        for char in text:
            if char == '\n':
                tokens.append(-1)  # NEWLINE token
            elif char == ' ':
                tokens.append(-2)  # SPACE token
            else:
                tokens.append(ord(char) % 256)
        return tokens

    async def _generate_strokes_autoregressive(
        self,
        tokens: List[int],
        style_embedding: np.ndarray
    ) -> List[Dict]:
        """Fast autoregressive stroke generation."""
        strokes = []
        
        for i, token in enumerate(tokens):
            # Generate stroke for this token
            if token < 0:
                # Special token (space, newline)
                strokes.append({
                    "type": "space" if token == -2 else "newline",
                    "points": []
                })
            else:
                # Regular character
                num_points = np.random.randint(5, 20)
                points = [
                    {
                        "x": float(x),
                        "y": float(y),
                        "pressure": float(p)
                    }
                    for x, y, p in zip(
                        np.linspace(0, 10, num_points),
                        np.linspace(0, 20, num_points) + np.random.randn(num_points) * 2,
                        np.random.uniform(0.5, 1.0, num_points)
                    )
                ]
                
                strokes.append({
                    "type": "glyph",
                    "character": chr(token),
                    "points": points
                })
        
        return strokes

    async def _generate_strokes_diffusion(
        self,
        tokens: List[int],
        style_embedding: np.ndarray
    ) -> List[Dict]:
        """Quality diffusion-based stroke generation."""
        # For now, fallback to autoregressive
        return await self._generate_strokes_autoregressive(tokens, style_embedding)

    async def _apply_layout_and_style(
        self,
        strokes: List[Dict],
        style_embedding: np.ndarray,
        pen_settings: Dict,
        page_settings: Dict
    ) -> List[Dict]:
        """Apply page layout and style to strokes."""
        margin_top = page_settings.get("margin_top", 50)
        margin_left = page_settings.get("margin_left", 50)
        line_height = page_settings.get("line_height", 25)
        
        x, y = margin_left, margin_top
        layout_strokes = []
        
        for stroke in strokes:
            if stroke["type"] == "newline":
                y += line_height
                x = margin_left
            elif stroke["type"] == "space":
                x += 15
            else:
                # Apply position and style
                for point in stroke["points"]:
                    point["x"] += x
                    point["y"] += y
                    # Apply pressure from pen settings
                    pressure_mult = pen_settings.get("pressure_multiplier", 1.0)
                    point["pressure"] *= pressure_mult
                
                layout_strokes.append(stroke)
                x += 12  # Character width
        
        return layout_strokes

    async def _paginate_strokes(self, strokes: List[Dict]) -> List[Dict]:
        """Split strokes into pages."""
        page_height = 1754  # A4 at 300 DPI
        page_width = 1240
        
        pages = []
        current_page = {
            "strokes": [],
            "height": page_height,
            "width": page_width
        }
        
        current_y = 0
        for stroke in strokes:
            max_y = max(p["y"] for p in stroke["points"]) if stroke["points"] else 0
            
            if max_y > page_height:
                # Start new page
                pages.append(current_page)
                current_page = {
                    "strokes": [],
                    "height": page_height,
                    "width": page_width
                }
                current_y = 0
            
            current_page["strokes"].append(stroke)
            current_y = max(current_y, max_y)
        
        if current_page["strokes"]:
            pages.append(current_page)
        
        return pages

    async def generate_with_equations(
        self,
        text: str,
        equations: List[str],
        style_embedding: np.ndarray
    ) -> Dict:
        """Generate handwriting with embedded LaTeX equations."""
        logger.info(f"Generating with {len(equations)} equations")
        
        return await self.generate_handwriting(
            style_embedding,
            text,
            mode="quality"
        )

    def generate_job_sync(self, job_id: str):
        """Synchronous wrapper for background job processing."""
        logger.info(f"Processing job {job_id}")

    async def get_job_progress(self, job_id: str) -> float:
        """Get progress of generation job."""
        return 0.0
