from app.core.firebase import db
from app.data.dto.generation_dto import GenerationJobDTO

class GenerationRepository:
    def get_job(self, job_id: str) -> GenerationJobDTO | None:
        doc = db.collection("generation_jobs").document(job_id).get()
        if not doc.exists:
            return None
        return GenerationJobDTO(job_id=job_id, **doc.to_dict())

    def update_job(self, job_id: str, data: dict):
        db.collection("generation_jobs").document(job_id).update(data)
