"""
Service for professor dashboard and final exam inscriptions.

Handles business logic that exists in professor views.
"""

from typing import Optional

from app.repositories import ProfessorRepository, SubjectRepository, FinalExamRepository, FinalExamInscriptionRepository


class ProfessorServiceError(Exception):
    """Base exception for professor operations."""
    pass


class ProfessorService:
    """
    Manages professor dashboard and final exam inscriptions.

    Business logic from professor views only.
    """

    def __init__(self,
                 professor_repository: Optional[ProfessorRepository] = None,
                 subject_repository: Optional[SubjectRepository] = None,
                 final_exam_repository: Optional[FinalExamRepository] = None,
                 final_exam_inscription_repository: Optional[FinalExamInscriptionRepository] = None):
        """Initialize with repositories."""
        self.professor_repository = professor_repository or ProfessorRepository()
        self.subject_repository = subject_repository or SubjectRepository()
        self.final_exam_repository = final_exam_repository or FinalExamRepository()
        self.final_exam_inscription_repository = final_exam_inscription_repository or FinalExamInscriptionRepository()

    def get_professor_dashboard_data(self, user):
        """
        Get data for professor dashboard.

        Business logic from professor_dashboard view.
        """
        try:
            professor = getattr(user, "professor", None)
            if not professor:
                raise ProfessorServiceError("Tu perfil de profesor no está configurado. Contactá a un administrador.")

            # Get assigned subjects (from view logic)
            subjects = self.subject_repository.list(filters={"professors": professor})

            # Get assigned finals (from view logic)
            finals = self.final_exam_repository.list(filters={"professors": professor}, select_related=["subject"])

            return {"subjects": subjects, "finals": finals}

        except Exception as e:
            if isinstance(e, ProfessorServiceError):
                raise
            raise ProfessorServiceError(f"Error getting dashboard data: {str(e)}") from e

    def get_final_exam_inscriptions(self, final_exam_id, professor):
        """
        Get final exam inscriptions for a professor's final.

        Business logic from professor_final_inscriptions view.
        """
        try:
            # Get final exam and validate professor assignment
            final_exam = self.final_exam_repository.get_by_id(final_exam_id)
            if not final_exam:
                raise ProfessorServiceError("Final exam not found")

            # Validate professor is assigned to this final
            # Check if professor is in the final's professors list
            final_professors = self.final_exam_repository.list(filters={"id": final_exam_id, "professors": professor})
            if not final_professors.exists():
                raise ProfessorServiceError("You are not assigned to this final exam")

            # Get inscriptions (from view logic)
            inscriptions = self.final_exam_inscription_repository.list(
                filters={"final_exam": final_exam},
                select_related=["student__user"],
                order_by=["student__user__last_name", "student__user__first_name"]
            )

            return {"final_exam": final_exam, "inscriptions": inscriptions}

        except Exception as e:
            if isinstance(e, ProfessorServiceError):
                raise
            raise ProfessorServiceError(f"Error getting final inscriptions: {str(e)}") from e
