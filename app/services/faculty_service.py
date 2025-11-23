"""
Service for faculty management operations.

Business logic for Faculty CRUD and dependency validation.
"""

from django.db import transaction
from typing import Dict, Any, Optional

from app.repositories import FacultyRepository, CareerRepository


class FacultyServiceError(Exception):
    """Base exception for faculty operations."""
    pass


class FacultyService:
    """
    Manages faculty entities.

    Business rules:
    - Faculty cannot be deleted if it has careers
    - All operations use repository pattern
    """

    def __init__(self,
                 faculty_repository: Optional[FacultyRepository] = None,
                 career_repository: Optional[CareerRepository] = None):
        # Repository dependencies
        self.faculty_repository = faculty_repository or FacultyRepository()
        self.career_repository = career_repository or CareerRepository()

    def create_faculty(self, faculty_data: Dict[str, Any]):
        """Create faculty via repository."""
        try:
            with transaction.atomic():
                return self.faculty_repository.create(faculty_data)
        except Exception as e:
            raise FacultyServiceError(f"Failed to create faculty: {str(e)}") from e

    def update_faculty(self, faculty, faculty_data: Dict[str, Any]):
        """Update faculty via repository."""
        try:
            with transaction.atomic():
                return self.faculty_repository.update(faculty, faculty_data)
        except Exception as e:
            raise FacultyServiceError(f"Failed to update faculty: {str(e)}") from e

    def delete_faculty(self, faculty):
        """
        Delete faculty after checking dependencies.

        Business rule: Faculty cannot be deleted if it has careers.
        """
        # Check dependencies via repository
        careers_in_faculty = self.career_repository.list_by_faculty(faculty.code)
        if careers_in_faculty.exists():
            raise FacultyServiceError(
                "Cannot delete faculty with existing careers. "
                "Delete or reassign careers first."
            )

        try:
            with transaction.atomic():
                self.faculty_repository.delete(faculty)
                return True
        except Exception as e:
            raise FacultyServiceError(f"Failed to delete faculty: {str(e)}") from e

    def get_faculty_by_code(self, code: str):
        """Get faculty by code via repository."""
        try:
            return self.faculty_repository.by_code(code)
        except Exception:
            return None

    def list_all_faculties(self):
        """List all faculties via repository."""
        return self.faculty_repository.list_all()
