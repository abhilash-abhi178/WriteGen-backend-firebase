# app/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    firebase_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firebase/firebase-adminsdk.json")
    firebase_bucket: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
    env: str = os.getenv("APP_ENV", "development")
    temp_dir: str = os.getenv("TEMP_DIR", "/tmp/writegen")

settings = Settings()
