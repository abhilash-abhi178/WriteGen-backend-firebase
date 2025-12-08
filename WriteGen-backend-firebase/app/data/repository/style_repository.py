from app.core.firebase import db
from app.data.dto.style_dto import StyleDTO

class StyleRepository:
    def get_style(self, style_id: str) -> StyleDTO | None:
        doc = db.collection("styles").document(style_id).get()
        if not doc.exists:
            return None
        return StyleDTO(id=style_id, **doc.to_dict())

    def update_style(self, style_id: str, data: dict):
        db.collection("styles").document(style_id).update(data)

    def list_styles(self, uid: str):
        q = db.collection("styles").where("uid", "==", uid).stream()
        return [StyleDTO(id=d.id, **d.to_dict()) for d in q]
