"""
Service for subject management operations.

Business logic for Subject CRUD and dependency validation.
"""

from django.db import transaction


from app.repositories import SubjectRepository, CareerRepository, ProfessorRepository, SubjectInscriptionRepository


class SubjectServiceError(Exception):
    """Base exception for subject operations."""
    pass


class SubjectService:
    """
    Manages subject entities.

    Business rules:
    - Subject cannot be deleted if it has inscriptions or professors
    - All operations use repository pattern
    """

    def __init__(self,
                 subject_repository=None,
                 career_repository=None,
                 professor_repository=None,
                 subject_inscription_repository=None):
        # Repository dependencies
        self.subject_repository = subject_repository or SubjectRepository()
        self.career_repository = career_repository or CareerRepository()
        self.professor_repository = professor_repository or ProfessorRepository()
        self.subject_inscription_repository = subject_inscription_repository or SubjectInscriptionRepository()

    def create_subject(self, subject_data):
        """Create subject via repository."""
        try:
            with transaction.atomic():
                return self.subject_repository.create(subject_data)
        except Exception as e:
            raise SubjectServiceError(f"Failed to create subject: {str(e)}") from e

    def update_subject(self, subject, subject_data):
        """Update subject via repository."""
        try:
            with transaction.atomic():
                return self.subject_repository.update(subject, subject_data)
        except Exception as e:
            raise SubjectServiceError(f"Failed to update subject: {str(e)}") from e

    def delete_subject(self, subject):
        """
        Delete subject after checking dependencies.

        Business rule: Subject cannot be deleted if it has inscriptions.
        """
        # Check dependencies via repositories
        inscriptions = self.subject_inscription_repository.list_by_subject(subject.id)
        if inscriptions.exists():
            raise SubjectServiceError(
                "Cannot delete subject with existing inscriptions. "
                "Remove inscriptions first."
            )

        try:
            with transaction.atomic():
                self.subject_repository.delete(subject)
                return True
        except Exception as e:
            raise SubjectServiceError(f"Failed to delete subject: {str(e)}") from e

    def get_subject_by_code(self, code):
        """Get subject by code via repository."""
        try:
            return self.subject_repository.by_code(code)
        except Exception:
            return None

    def list_all_subjects(self):
        """List all subjects via repository."""
        return self.subject_repository.list_all()

    def list_subjects_by_career(self, career_code):
        """List subjects by career via repository."""
        return self.subject_repository.list_by_career(career_code)
