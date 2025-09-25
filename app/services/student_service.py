"""
Service for student dashboard and profile management.

Handles the business logic that exists in student views.
"""

from typing import Optional

from app.repositories import (
    StudentRepository, SubjectRepository, SubjectInscriptionRepository,
    GradeRepository, FinalExamRepository, FinalExamInscriptionRepository
)


class StudentServiceError(Exception):
    """Base exception for student operations."""
    pass


class StudentService:
    """
    Manages student dashboard and profile operations.

    Mirrors the business logic that exists in the original student views.
    """

    def __init__(self,
                 student_repository: Optional[StudentRepository] = None,
                 subject_repository: Optional[SubjectRepository] = None,
                 subject_inscription_repository: Optional[SubjectInscriptionRepository] = None,
                 grade_repository: Optional[GradeRepository] = None,
                 final_exam_repository: Optional[FinalExamRepository] = None,
                 final_exam_inscription_repository: Optional[FinalExamInscriptionRepository] = None):
        """Initialize with repositories."""
        self.student_repository = student_repository or StudentRepository()
        self.subject_repository = subject_repository or SubjectRepository()
        self.subject_inscription_repository = subject_inscription_repository or SubjectInscriptionRepository()
        self.grade_repository = grade_repository or GradeRepository()
        self.final_exam_repository = final_exam_repository or FinalExamRepository()
        self.final_exam_inscription_repository = final_exam_inscription_repository or FinalExamInscriptionRepository()

    def get_student_dashboard_data(self, user):
        """
        Get all data needed for student dashboard.

        Business logic from student_dashboard view.
        """
        # Get student profile
        try:
            student = getattr(user, "student", None)
            if not student:
                raise StudentServiceError("Tu perfil de estudiante no está configurado. Contactá a un administrador.")

            # Get subjects for student's career
            subjects = self.subject_repository.list(filters={"career": student.career})

            # Get student inscriptions
            inscriptions = self.subject_inscription_repository.list(
                filters={"student": student},
                select_related=["subject"]
            )

            # Get inscribed subject codes
            inscribed_subject_codes = list(inscriptions.values_list("subject__code", flat=True))

            # Get student grades
            grades = self.grade_repository.list(filters={"student": student}, select_related=["subject"])

            # Get eligible finals (where status is REGULAR)
            # This needs to be done through repository
            eligible_grades = self.grade_repository.list(
                filters={"student": student, "status": "REGULAR"}  # Grade.StatusSubject.REGULAR
            )
            eligible_subject_ids = [grade.subject_id for grade in eligible_grades]
            eligible_finals = self.final_exam_repository.list(filters={"subject_id__in": eligible_subject_ids})

            # Get final exam inscriptions
            final_inscriptions = self.final_exam_inscription_repository.list(
                filters={"student": student},
                select_related=["final_exam__subject"],
                order_by=["final_exam__date"]
            )

            # Get inscribed final IDs
            inscribed_final_ids = list(final_inscriptions.values_list("final_exam_id", flat=True))

            return {
                "subjects": subjects,
                "inscriptions": inscriptions,
                "grades": grades,
                "eligible_finals": eligible_finals,
                "final_inscriptions": final_inscriptions,
                "inscribed_final_ids": inscribed_final_ids,
                "inscribed_subject_codes": inscribed_subject_codes
            }

        except Exception as e:
            if isinstance(e, StudentServiceError):
                raise
            raise StudentServiceError(f"Error getting dashboard data: {str(e)}") from e
