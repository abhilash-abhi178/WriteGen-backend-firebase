from app.core.firebase import db
from app.data.dto.user_dto import UserDTO

class UserRepository:
    def get_user(self, uid: str) -> UserDTO | None:
        doc = db.collection("users").document(uid).get()
        if not doc.exists:
            return None
        return UserDTO(**doc.to_dict())

    def create_user(self, user: UserDTO):
        db.collection("users").document(user.uid).set(user.dict())
        return True

    def update_user(self, uid: str, data: dict):
        db.collection("users").document(uid).update(data)
        return True
