"""
Service for career management operations.

Business logic for Career CRUD and dependency validation.
"""

from django.db import transaction
from typing import Dict, Any, Optional

from app.repositories import CareerRepository, StudentRepository, SubjectRepository


class CareerServiceError(Exception):
    """Base exception for career operations."""
    pass


class CareerService:
    """
    Manages career entities.

    Business rules:
    - Career cannot be deleted if it has students
    - All operations use repository pattern
    """

    def __init__(self,
                 career_repository: Optional[CareerRepository] = None,
                 faculty_repository=None,  # Keep for compatibility
                 student_repository: Optional[StudentRepository] = None,
                 subject_repository: Optional[SubjectRepository] = None):
        # Repository dependencies
        self.career_repository = career_repository or CareerRepository()
        self.student_repository = student_repository or StudentRepository()
        self.subject_repository = subject_repository or SubjectRepository()

    def create_career(self, career_data: Dict[str, Any]):
        """Create career via repository."""
        try:
            with transaction.atomic():
                return self.career_repository.create(career_data)
        except Exception as e:
            raise CareerServiceError(f"Failed to create career: {str(e)}") from e

    def update_career(self, career, career_data: Dict[str, Any]):
        """Update career via repository."""
        try:
            with transaction.atomic():
                return self.career_repository.update(career, career_data)
        except Exception as e:
            raise CareerServiceError(f"Failed to update career: {str(e)}") from e

    def delete_career(self, career):
        """
        Delete career after checking dependencies.

        Business rule: Career cannot be deleted if it has students.
        """
        # Check dependencies via repositories
        students_in_career = self.student_repository.list_by_career(career.code)
        if students_in_career.exists():
            raise CareerServiceError(
                "Cannot delete career with existing students. "
                "Delete or reassign students first."
            )

        try:
            with transaction.atomic():
                self.career_repository.delete(career)
                return True
        except Exception as e:
            raise CareerServiceError(f"Failed to delete career: {str(e)}") from e

    def get_career_by_code(self, code: str):
        """Get career by code via repository."""
        try:
            return self.career_repository.by_code(code)
        except Exception:
            return None

    def list_all_careers(self):
        """List all careers via repository."""
        return self.career_repository.list_all()

    def list_careers_by_faculty(self, faculty_code: str):
        """List careers by faculty via repository."""
        return self.career_repository.list_by_faculty(faculty_code)
