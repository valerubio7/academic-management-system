from .base import BaseRepository
from app.models.final_exam import FinalExam


class FinalExamRepository(BaseRepository):
    """Repository for FinalExam model access."""

    def __init__(self):
        super().__init__(FinalExam)

    def list_all_with_subject(self):
        """List all final exams with subject selected, ordered by date descending."""
        return self.list(select_related=("subject",), order_by=("-date",))

    def by_id_with_subject(self, pk):
        """Retrieve a final exam by ID with subject selected.

        Args:
            pk: The primary key.

        Returns:
            The FinalExam instance.
        """
        return self.get_by_id(pk, select_related=("subject",))

    def list_by_subject_ids(self, subject_ids):
        """List final exams by subject IDs, ordered by date.

        Args:
            subject_ids: List of subject IDs.

        Returns:
            Queryset of FinalExam instances.
        """
        return self.list(filters={"subject_id__in": subject_ids}, order_by=("date",))

    def list_by_subject(self, subject_code):
        """List final exams by subject code, ordered by date.

        Args:
            subject_code: The subject code.

        Returns:
            Queryset of FinalExam instances.
        """
        return self.list(filters={"subject_id": subject_code}, order_by=("date",))
