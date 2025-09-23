from .base import BaseRepository
from app.models.final_exam_inscription import FinalExamInscription


class FinalExamInscriptionRepository(BaseRepository):
    def __init__(self):
        super().__init__(FinalExamInscription)

    def get_or_create(self, *, student_id, final_exam_id):
        return self.model.objects.get_or_create(student_id=student_id, final_exam_id=final_exam_id)

    def list_for_final_with_student_user(self, final_exam_id):
        return self.list(filters={"final_exam_id": final_exam_id}, select_related=("student__user",), order_by=("student__user__last_name", "student__user__first_name"))

    def list_ids_for_student(self, student_id):
        return list(self.get_queryset().filter(student_id=student_id).values_list("final_exam_id", flat=True))
