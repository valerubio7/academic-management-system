from .base import BaseRepository
from app.models.student import Student


class StudentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Student)

    def by_user_id_with_career_faculty(self, user_id):
        qs = self.list(filters={"user_id": user_id}, select_related=("career__faculty",))
        return qs.first()

    def list_by_career(self, career_code):
        return self.list(filters={"career__code": career_code}, select_related=("user",))
