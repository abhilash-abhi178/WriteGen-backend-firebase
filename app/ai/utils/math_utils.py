# app/ai/utils/math_utils.py
import math
from typing import Tuple

def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])

def clamp(val: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, val))
