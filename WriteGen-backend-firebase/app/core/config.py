# app/core/config.py
import os


class Settings:
    """Lightweight settings container that reads from environment variables.

    This avoids depending on pydantic BaseSettings at runtime so the
    application can run with multiple pydantic versions.
    """

    def __init__(self):
        self.firebase_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firebase/firebase-adminsdk.json")
        self.firebase_bucket: str = os.getenv("FIREBASE_STORAGE_BUCKET", "")
        self.env: str = os.getenv("APP_ENV", "development")
        self.temp_dir: str = os.getenv("TEMP_DIR", "/tmp/writegen")

    def get(self, key: str, default=None):
        return getattr(self, key, default)


settings = Settings()
