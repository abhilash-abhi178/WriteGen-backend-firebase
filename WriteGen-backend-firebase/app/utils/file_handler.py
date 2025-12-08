# app/utils/file_handler.py
import os
from uuid import uuid4
from datetime import datetime

def tmp_filename(prefix="upload", suffix=""):
    base = f"{prefix}_{datetime.utcnow().timestamp()}_{uuid4().hex}"
    if suffix:
        return f"/tmp/{base}.{suffix}"
    return f"/tmp/{base}"
