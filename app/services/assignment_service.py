"""
Service for professor assignment operations.

Handles business logic for assigning professors to subjects and final exams.
"""

from django.db import transaction
from typing import Optional, List

from app.repositories import SubjectRepository, FinalExamRepository, ProfessorRepository


class AssignmentServiceError(Exception):
    """Base exception for assignment operations."""
    pass


class AssignmentService:
    """
    Manages professor assignments to subjects and final exams.

    Business logic from assign_subject_professors and assign_final_professors views.
    """

    def __init__(self,
                 subject_repository: Optional[SubjectRepository] = None,
                 final_exam_repository: Optional[FinalExamRepository] = None,
                 professor_repository: Optional[ProfessorRepository] = None):
        """Initialize with repositories."""
        self.subject_repository = subject_repository or SubjectRepository()
        self.final_exam_repository = final_exam_repository or FinalExamRepository()
        self.professor_repository = professor_repository or ProfessorRepository()

    def update_subject_professor_assignments(self, subject_code: str, selected_professor_ids: List[str]) -> dict:
        """
        Update professor assignments for a subject.

        Business logic from assign_subject_professors view.
        """
        try:
            with transaction.atomic():
                # Get subject
                subject = self.subject_repository.by_code(subject_code)
                if not subject:
                    raise AssignmentServiceError(f"Subject {subject_code} not found")

                # Convert to sets for comparison (from view logic)
                selected_ids = set(selected_professor_ids)
                # Get current professor IDs through the M2M relation (acceptable for this operation)
                current_ids = set(subject.professors.values_list("pk", flat=True))

                # Calculate changes (from view logic)
                to_add = selected_ids - current_ids
                to_remove = current_ids - selected_ids

                # Apply changes (from view logic)
                changes_made = False
                if to_add or to_remove:
                    if to_add:
                        subject.professors.add(*to_add)
                    if to_remove:
                        subject.professors.remove(*to_remove)
                    changes_made = True

                message = ("Asignaciones actualizadas correctamente." if changes_made
                           else "No hubo cambios en las asignaciones.")

                return {"success": True, "changes_made": changes_made, "message": message}

        except Exception as e:
            if isinstance(e, AssignmentServiceError):
                raise
            raise AssignmentServiceError(f"Failed to update subject assignments: {str(e)}") from e

    def update_final_professor_assignments(self, final_exam_id: int, selected_professor_ids: List[str]) -> dict:
        """
        Update professor assignments for a final exam.

        Business logic from assign_final_professors view.
        """
        try:
            with transaction.atomic():
                # Get final exam
                final_exam = self.final_exam_repository.get_by_id(final_exam_id)
                if not final_exam:
                    raise AssignmentServiceError(f"Final exam {final_exam_id} not found")

                # Convert to sets for comparison (from view logic)
                selected_ids = set(selected_professor_ids)
                # Get current professor IDs through the M2M relation (acceptable for this operation)
                current_ids = set(final_exam.professors.values_list("pk", flat=True))

                # Calculate changes (from view logic)
                to_add = selected_ids - current_ids
                to_remove = current_ids - selected_ids

                # Apply changes (from view logic)
                changes_made = False
                if to_add or to_remove:
                    if to_add:
                        final_exam.professors.add(*to_add)
                    if to_remove:
                        final_exam.professors.remove(*to_remove)
                    changes_made = True

                message = ("Asignaciones del final actualizadas correctamente." if changes_made
                           else "No hubo cambios en las asignaciones.")

                return {"success": True, "changes_made": changes_made, "message": message}

        except Exception as e:
            if isinstance(e, AssignmentServiceError):
                raise
            raise AssignmentServiceError(f"Failed to update final assignments: {str(e)}") from e

    def get_all_professors(self):
        """
        Get all professors for assignment forms.

        From both assign views.
        """
        return self.professor_repository.list(select_related=["user"])
