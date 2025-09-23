from django.db import transaction

from .base import BaseRepository
from app.models.grade import Grade


class GradeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Grade)

    def for_student_with_subject(self, student_id):
        return self.list(filters={"student_id": student_id}, select_related=("subject",))

    def latest_for_student_subject(self, student_id, subject_code):
        qs = self.list(filters={"student_id": student_id, "subject_id": subject_code}, order_by=("-id",))
        return qs.first()

    def for_subject_with_student_user(self, subject_code):
        return self.list(filters={"subject_id": subject_code}, select_related=("student__user",), order_by=("student__user__last_name", "student__user__first_name"))
