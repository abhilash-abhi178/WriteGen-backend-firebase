# app/core/config.py
import os
from typing import Optional
from enum import Enum
from dotenv import load_dotenv
import json

# Load .env file
load_dotenv()


class ProcessingMode(str, Enum):
    """Processing mode enum for handwriting generation."""
    CLOUD = "cloud"
    HYBRID = "hybrid"
    LOCAL_ONLY = "local_only"


class GenerationMode(str, Enum):
    """Generation mode: fast (autoregressive) vs quality (diffusion)."""
    FAST = "fast"
    QUALITY = "quality"


class PageTemplate(str, Enum):
    """Page template types."""
    BLANK = "blank"
    RULED = "ruled"
    GRID = "grid"
    DOTTED = "dotted"
    YELLOW_EXAM = "yellow_exam"
    EXAM_SHEET = "exam_sheet"


class PenType(str, Enum):
    """Pen type options."""
    BALLPOINT = "ballpoint"
    GEL = "gel"
    FOUNTAIN = "fountain"
    FELT_TIP = "felt_tip"


class ExportFormat(str, Enum):
    """Export format options."""
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Firebase Configuration
        self.firebase_project_id = os.getenv("FIREBASE_PROJECT_ID", "writegen-7b3c3")
        self.firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL", "")
        self.firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
        self.firebase_storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET", f"{self.firebase_project_id}.appspot.com")
        
        # Environment
        self.env = os.getenv("ENVIRONMENT", "development")
        self.debug = self.env == "development"
        self.api_version = os.getenv("API_VERSION", "v1")
        
        # Storage & Directories
        self.temp_dir = os.getenv("TEMP_DIR", "/tmp/writegen")
        self.samples_dir = os.path.join(self.temp_dir, "samples")
        self.models_dir = os.path.join(self.temp_dir, "models")
        self.output_dir = os.path.join(self.temp_dir, "output")
        
        # Ensure directories exist
        for directory in [self.samples_dir, self.models_dir, self.output_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Database Configuration
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///writegen.db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        
        # ML Model Configuration
        self.model_path = os.getenv("MODEL_PATH", os.path.join(self.models_dir, "handwriting_model.pt"))
        self.style_encoder_path = os.getenv("STYLE_ENCODER_PATH", os.path.join(self.models_dir, "style_encoder.pt"))
        self.stroke_generator_path = os.getenv("STROKE_GENERATOR_PATH", os.path.join(self.models_dir, "stroke_generator.pt"))
        
        # GPU Configuration
        self.use_gpu = os.getenv("USE_GPU", "false").lower() == "true"
        self.device = "cuda" if self.use_gpu else "cpu"
        
        # Processing Configuration
        self.max_sample_size_mb = int(os.getenv("MAX_SAMPLE_SIZE_MB", "50"))
        self.max_document_length_chars = int(os.getenv("MAX_DOCUMENT_LENGTH_CHARS", "10000"))
        self.generation_timeout_seconds = int(os.getenv("GENERATION_TIMEOUT_SECONDS", "300"))
        
        # Feature Flags
        self.enable_signature_generation = os.getenv("ENABLE_SIGNATURES", "true").lower() == "true"
        self.enable_exam_generator = os.getenv("ENABLE_EXAM_GENERATOR", "true").lower() == "true"
        self.enable_diagram_support = os.getenv("ENABLE_DIAGRAMS", "true").lower() == "true"
        self.enable_math_support = os.getenv("ENABLE_EQUATIONS", "true").lower() == "true"
        self.enable_batch_generation = os.getenv("ENABLE_BATCH", "true").lower() == "true"
        
        # Rate Limiting
        self.rate_limit_requests_per_minute = int(os.getenv("RATE_LIMIT_RPM", "60"))
        self.rate_limit_pages_per_day = {
            "free": 10,
            "hobby": 100,
            "pro": 1000,
            "enterprise": -1
        }
        
        # CORS Configuration
        cors_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:8100,http://10.0.2.2:8000")
        self.allowed_origins = [origin.strip() for origin in cors_origins.split(",")]
        
        # Server Configuration
        self.port = int(os.getenv("PORT", "8000"))
        self.host = os.getenv("HOST", "0.0.0.0")
        
    def get(self, key: str, default=None):
        """Get configuration value by key."""
        return getattr(self, key, default)


# Global settings instance
settings = Settings()
