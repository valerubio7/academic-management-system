"""
Service for final exam management operations.

Business logic for FinalExam CRUD and dependency validation.
"""

from django.db import transaction

from app.repositories import FinalExamRepository, SubjectRepository, ProfessorRepository, FinalExamInscriptionRepository


class FinalExamServiceError(Exception):
    """Base exception for final exam operations."""
    pass


class FinalExamService:
    """
    Manages final exam entities.

    Business rules:
    - Final exam cannot be deleted if it has inscriptions
    - All operations use repository pattern
    """

    def __init__(self,
                 final_exam_repository=None,
                 subject_repository=None,
                 professor_repository=None,
                 final_exam_inscription_repository=None):
        # Repository dependencies
        self.final_exam_repository = final_exam_repository or FinalExamRepository()
        self.subject_repository = subject_repository or SubjectRepository()
        self.professor_repository = professor_repository or ProfessorRepository()
        self.final_exam_inscription_repository = final_exam_inscription_repository or FinalExamInscriptionRepository()

    def create_final_exam(self, final_exam_data):
        """Create final exam via repository."""
        try:
            with transaction.atomic():
                return self.final_exam_repository.create(final_exam_data)
        except Exception as e:
            raise FinalExamServiceError(f"Failed to create final exam: {str(e)}") from e

    def update_final_exam(self, final_exam, final_exam_data):
        """Update final exam via repository."""
        try:
            with transaction.atomic():
                return self.final_exam_repository.update(final_exam, final_exam_data)
        except Exception as e:
            raise FinalExamServiceError(f"Failed to update final exam: {str(e)}") from e

    def delete_final_exam(self, final_exam):
        """
        Delete final exam after checking dependencies.

        Business rule: Final exam cannot be deleted if it has inscriptions.
        """
        # Check dependencies via repositories
        inscriptions = self.final_exam_inscription_repository.list_by_final_exam(final_exam.id)
        if inscriptions.exists():
            raise FinalExamServiceError(
                "Cannot delete final exam with existing inscriptions. "
                "Remove inscriptions first."
            )

        try:
            with transaction.atomic():
                self.final_exam_repository.delete(final_exam)
                return True
        except Exception as e:
            raise FinalExamServiceError(f"Failed to delete final exam: {str(e)}") from e

    def get_final_exam_by_id(self, final_exam_id):
        """Get final exam by ID via repository."""
        try:
            return self.final_exam_repository.get_by_id(final_exam_id)
        except Exception:
            return None

    def list_all_final_exams(self):
        """List all final exams via repository."""
        return self.final_exam_repository.list_all()

    def list_final_exams_by_subject(self, subject_code):
        """List final exams by subject via repository."""
        return self.final_exam_repository.list_by_subject(subject_code)
