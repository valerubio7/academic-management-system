from .base import BaseRepository
from app.models.subject_inscription import SubjectInscription


class SubjectInscriptionRepository(BaseRepository):
    def __init__(self):
        super().__init__(SubjectInscription)

    def get_or_create(self, *, student_id, subject_code):
        return self.model.objects.get_or_create(student_id=student_id, subject_id=subject_code)

    def list_for_student_with_subject(self, student_id):
        return self.list(filters={"student_id": student_id}, select_related=("subject",))

    def list_subject_codes_for_student(self, student_id):
        return list(self.get_queryset().filter(student_id=student_id).values_list("subject__code", flat=True))
