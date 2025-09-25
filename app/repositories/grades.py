from .base import BaseRepository
from app.models.grade import Grade


class GradeRepository(BaseRepository):
    """Repository for Grade model access."""

    def __init__(self):
        super().__init__(Grade)

    def for_student_with_subject(self, student_id):
        """List grades for a student with subject selected.

        Args:
            student_id: The student ID.

        Returns:
            Queryset of Grade instances.
        """
        return self.list(filters={"student_id": student_id}, select_related=("subject",))

    def latest_for_student_subject(self, student_id, subject_code):
        """Get the latest grade for a student and subject.

        Args:
            student_id: The student ID.
            subject_code: The subject code.

        Returns:
            The latest Grade instance or None.
        """
        qs = self.list(filters={"student_id": student_id, "subject_id": subject_code}, order_by=("-id",))
        return qs.first()

    def for_subject_with_student_user(self, subject_code):
        """List grades for a subject with student user selected.

        Args:
            subject_code: The subject code.

        Returns:
            Queryset of Grade instances.
        """
        return self.list(filters={"subject_id": subject_code}, select_related=("student__user",), order_by=("student__user__last_name", "student__user__first_name"))

    def list_by_subject(self, subject_code):
        """List grades by subject code.

        Args:
            subject_code: The subject code.

        Returns:
            Queryset of Grade instances.
        """
        return self.list(filters={"subject_id": subject_code})

    def get_or_create(self, *, student_id, subject_code):
        """Get or create a grade record.

        Args:
            student_id: The student ID.
            subject_code: The subject code.

        Returns:
            Tuple of (instance, created).
        """
        return self.model.objects.get_or_create(student_id=student_id, subject_id=subject_code)
