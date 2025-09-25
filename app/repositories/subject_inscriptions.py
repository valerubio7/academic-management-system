from .base import BaseRepository
from app.models.subject_inscription import SubjectInscription


class SubjectInscriptionRepository(BaseRepository):
    """Repository for SubjectInscription model access."""

    def __init__(self):
        super().__init__(SubjectInscription)

    def get_or_create(self, *, student_id, subject_code):
        """Get or create a subject inscription.

        Args:
            student_id: The student ID.
            subject_code: The subject code.

        Returns:
            Tuple of (instance, created).
        """
        return self.model.objects.get_or_create(student_id=student_id, subject_id=subject_code)

    def list_for_student_with_subject(self, student_id):
        """List subject inscriptions for a student with subject selected.

        Args:
            student_id: The student ID.

        Returns:
            Queryset of SubjectInscription instances.
        """
        return self.list(filters={"student_id": student_id}, select_related=("subject",))

    def list_subject_codes_for_student(self, student_id):
        """List subject codes for a student.

        Args:
            student_id: The student ID.

        Returns:
            List of subject codes.
        """
        return list(self.get_queryset().filter(student_id=student_id).values_list("subject__code", flat=True))

    def list_by_subject(self, subject_code):
        """List subject inscriptions by subject code.

        Args:
            subject_code: The subject code.

        Returns:
            Queryset of SubjectInscription instances.
        """
        return self.list(filters={"subject_id": subject_code})
