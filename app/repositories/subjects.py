from .base import BaseRepository
from app.models.subject import Subject


class SubjectRepository(BaseRepository):
    def __init__(self):
        super().__init__(Subject)

    def list_all_with_career(self):
        return self.list(select_related=("career",), order_by=("career__name", "name"))

    def by_code_with_career(self, code):
        return self.get_one({"code": code}, select_related=("career",))

    def list_by_career(self, career_code):
        return self.list(filters={"career__code": career_code}, order_by=("year", "name"))
