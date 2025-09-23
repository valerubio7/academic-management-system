from .base import BaseRepository
from app.models.career import Career


class CareerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Career)

    def list_all(self):
        return self.list(order_by=("name",), select_related=("faculty",))

    def by_code(self, code):
        return self.get_one({"code": code}, select_related=("faculty",))

    def list_by_faculty(self, faculty_code):
        return self.list(filters={"faculty__code": faculty_code}, order_by=("name",))
