from app.core.firebase import db
from app.data.dto.sample_dto import SampleDTO

class SampleRepository:
    def get_sample(self, sid: str) -> SampleDTO | None:
        doc = db.collection("samples").document(sid).get()
        if not doc.exists:
            return None
        return SampleDTO(id=sid, **doc.to_dict())

    def update_sample(self, sid: str, data: dict):
        db.collection("samples").document(sid).update(data)
        return True

    def list_user_samples(self, uid: str):
        q = db.collection("samples").where("uid", "==", uid).stream()
        return [SampleDTO(id=d.id, **d.to_dict()) for d in q]
