from app.services.image_processor import ImageProcessor
from app.services.style_service import StyleService
from app.services.ocr_service import OCRService
from app.services.generation_service import GenerationService
from app.services.export_service import ExportService

image_processor = ImageProcessor()
style_service = StyleService()
ocr_service = OCRService()
generation_service = GenerationService()
export_service = ExportService()
