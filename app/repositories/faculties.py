from .base import BaseRepository
from app.models.faculty import Faculty


class FacultyRepository(BaseRepository):
    def __init__(self):
        super().__init__(Faculty)

    def list_all(self):
        return self.list(order_by=("name",))

    def by_code(self, code):
        return self.get_one({"code": code})
