from .base import BaseRepository
from app.models.final_exam_inscription import FinalExamInscription


class FinalExamInscriptionRepository(BaseRepository):
    """Repository for FinalExamInscription model access."""

    def __init__(self):
        super().__init__(FinalExamInscription)

    def get_or_create(self, *, student_id, final_exam_id):
        """Get or create a final exam inscription.

        Args:
            student_id: The student ID.
            final_exam_id: The final exam ID.

        Returns:
            Tuple of (instance, created).
        """
        return self.model.objects.get_or_create(student_id=student_id, final_exam_id=final_exam_id)

    def list_for_final_with_student_user(self, final_exam_id):
        """List inscriptions for a final exam with student user selected.

        Args:
            final_exam_id: The final exam ID.

        Returns:
            Queryset of FinalExamInscription instances.
        """
        return self.list(filters={"final_exam_id": final_exam_id}, select_related=("student__user",), order_by=("student__user__last_name", "student__user__first_name"))

    def list_ids_for_student(self, student_id):
        """List final exam IDs for a student.

        Args:
            student_id: The student ID.

        Returns:
            List of final exam IDs.
        """
        return list(self.get_queryset().filter(student_id=student_id).values_list("final_exam_id", flat=True))
