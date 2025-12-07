"""Document generation and export schemas."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, UUID4


class PageTemplate(str, Enum):
    BLANK = "blank"
    RULED = "ruled"
    GRID = "grid"
    DOTTED = "dotted"
    YELLOW_EXAM = "yellow_exam"
    EXAM_SHEET = "exam_sheet"


class ExportFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"
    SVG = "svg"


class GenerationMode(str, Enum):
    FAST = "fast"  # Autoregressive, lower latency
    QUALITY = "quality"  # Diffusion-based, higher fidelity


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PageSettings(BaseModel):
    """Page layout and template settings."""
    template: PageTemplate = PageTemplate.RULED
    margin_top_mm: float = 20.0
    margin_bottom_mm: float = 20.0
    margin_left_mm: float = 20.0
    margin_right_mm: float = 20.0
    line_spacing_mm: float = 8.0


class PenSettings(BaseModel):
    """Pen and ink customization."""
    ink_color: str = "black"  # "black", "blue", "red"
    pen_type: str = "ballpoint"  # "ballpoint", "gel", "fountain", "felt_tip"
    stroke_thickness_mm: float = 0.7
    realism: float = 0.8  # 0.0 to 1.0
    imperfection: float = 0.5  # 0.0 to 1.0


class EquationBlock(BaseModel):
    """LaTeX equation block."""
    equation_id: UUID4
    latex_content: str
    position_line: int
    position_col: int


class DiagramBlock(BaseModel):
    """Diagram or shape block."""
    diagram_id: UUID4
    diagram_type: str  # "simple_shapes", "chemical", "circuit", "freehand"
    diagram_data: bytes
    position_line: int


class DocumentInput(BaseModel):
    """Input document for generation."""
    title: str
    content: str
    equations: List[EquationBlock] = []
    diagrams: List[DiagramBlock] = []


class GenerationJobResult(BaseModel):
    """Generation job result."""
    output_s3_path: str
    page_paths: List[str]
    page_count: int
    status_message: str


class GenerationJobCreate(BaseModel):
    """Generation job creation request."""
    style_id: UUID4
    document: DocumentInput
    page_settings: PageSettings
    pen_settings: PenSettings
    mode: GenerationMode = GenerationMode.FAST
    requested_formats: List[ExportFormat] = [ExportFormat.PDF]


class GenerationJob(BaseModel):
    """Generation job response."""
    job_id: UUID4
    user_id: UUID4
    style_id: UUID4
    status: JobStatus
    input: DocumentInput
    page_settings: PageSettings
    pen_settings: PenSettings
    mode: GenerationMode
    requested_formats: List[ExportFormat]
    result: Optional[GenerationJobResult] = None
    error_message: Optional[str] = None
    progress_percent: float = 0.0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job-550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-550e8400-e29b-41d4-a716-446655440001",
                "style_id": "style-550e8400-e29b-41d4-a716-446655440002",
                "status": "completed",
                "progress_percent": 100.0,
                "result": {
                    "page_count": 3,
                    "output_s3_path": "outputs/job-123/",
                    "page_paths": ["page-1.pdf", "page-2.pdf", "page-3.pdf"]
                }
            }
        }


class ExportSettings(BaseModel):
    """Export configuration."""
    dpi: int = 300
    color_profile: str = "srgb"  # "srgb", "cmyk"
    include_watermark: bool = False
    bleed_mm: float = 3.0
    crop_marks: bool = False


class BatchGenerationRequest(BaseModel):
    """Batch generation request."""
    style_id: UUID4
    documents: List[DocumentInput]
    page_settings: PageSettings
    pen_settings: PenSettings
    mode: GenerationMode = GenerationMode.FAST
