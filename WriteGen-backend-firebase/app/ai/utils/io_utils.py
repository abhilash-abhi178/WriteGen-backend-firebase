# app/ai/utils/io_utils.py
import os
from typing import BinaryIO

def save_bytes(path: str, data: bytes) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
