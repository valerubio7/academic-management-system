"""
Service for grade management operations.

Handles business logic that exists in professor grade views.
"""

from django.db import transaction
from typing import Optional

from app.repositories import GradeRepository, SubjectInscriptionRepository, StudentRepository, SubjectRepository


class GradeServiceError(Exception):
    """Base exception for grade operations."""
    pass


class GradeService:
    """
    Manages grade operations based on professor views logic.

    Business logic from grade_list and grade_edit views.
    """

    def __init__(self,
                 grade_repository: Optional[GradeRepository] = None,
                 subject_inscription_repository: Optional[SubjectInscriptionRepository] = None,
                 student_repository: Optional[StudentRepository] = None,
                 subject_repository: Optional[SubjectRepository] = None):
        """Initialize with repositories."""
        self.grade_repository = grade_repository or GradeRepository()
        self.subject_inscription_repository = subject_inscription_repository or SubjectInscriptionRepository()
        self.student_repository = student_repository or StudentRepository()
        self.subject_repository = subject_repository or SubjectRepository()

    def get_subject_grades_with_backfill(self, subject, professor):
        """
        Get grades for a subject and backfill missing Grade entries.

        Business logic from grade_list view.
        """
        try:
            with transaction.atomic():
                # Get enrolled students (from view logic)
                enrolled_student_ids = set(
                    self.subject_inscription_repository.list(
                        filters={"subject": subject}
                    ).values_list("student_id", flat=True)
                )

                # Get existing grade student IDs
                existing_grade_student_ids = set(
                    self.grade_repository.list(
                        filters={"subject": subject}
                    ).values_list("student_id", flat=True)
                )

                # Find missing IDs and create grades
                missing_ids = enrolled_student_ids - existing_grade_student_ids
                if missing_ids:
                    grades_to_create = []
                    for student_id in missing_ids:
                        grades_to_create.append({'student_id': student_id, 'subject': subject})
                    # Bulk create missing grades
                    for grade_data in grades_to_create:
                        self.grade_repository.create(grade_data)

                # Return ordered grades
                return self.grade_repository.list(
                    filters={"subject": subject},
                    select_related=["student__user"],
                    order_by=["student__user__last_name", "student__user__first_name"]
                )

        except Exception as e:
            raise GradeServiceError(f"Failed to get subject grades: {str(e)}") from e

    def update_grade(self, grade, grade_data):
        """
        Update a grade record.

        Business logic from grade_edit view.
        """
        try:
            with transaction.atomic():
                # Check if status was changed (from view logic)
                status_was_changed = "status" in grade_data

                # Update grade via repository
                updated_grade = self.grade_repository.update(grade, grade_data)

                # Update status if not manually changed (from view logic)
                if not status_was_changed:
                    # This calls the model's update_status method
                    updated_grade.update_status()

                return updated_grade

        except Exception as e:
            raise GradeServiceError(f"Failed to update grade: {str(e)}") from e

    def validate_grade_edit_permissions(self, grade, professor):
        """
        Validate professor permissions to edit a grade.

        Business logic from grade_edit view guards.
        """
        # Professor must be assigned to the subject
        professor_subjects = self.subject_repository.list(filters={"professors": professor})
        if grade.subject not in professor_subjects:
            raise GradeServiceError("No puede editar notas de materias no asignadas.")

        # Student must be inscribed in the subject
        inscription_exists = self.subject_inscription_repository.exists(
            filters={"student": grade.student, "subject": grade.subject}
        )
        if not inscription_exists:
            raise GradeServiceError("Solo puede calificar a estudiantes inscriptos en la materia.")

        return True
