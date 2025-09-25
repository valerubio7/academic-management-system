"""
Service for inscription management operations.

Business logic for subject and final exam inscriptions.
Handles eligibility validation and enrollment rules.
"""

from django.db import transaction

from app.repositories import (
    SubjectInscriptionRepository,
    FinalExamInscriptionRepository,
    StudentRepository,
    SubjectRepository,
    FinalExamRepository,
    GradeRepository
)


class InscriptionServiceError(Exception):
    """Base exception for inscription operations."""
    pass


class InscriptionService:
    """
    Manages student inscriptions to subjects and final exams.

    Business rules:
    - Students can only inscribe to subjects in their career
    - Final exam inscription requires subject inscription
    - No duplicate inscriptions allowed
    """

    def __init__(self,
                 subject_inscription_repository=None,
                 final_exam_inscription_repository=None,
                 student_repository=None,
                 subject_repository=None,
                 final_exam_repository=None,
                 grade_repository=None):
        # Repository dependencies
        self.subject_inscription_repository = subject_inscription_repository or SubjectInscriptionRepository()
        self.final_exam_inscription_repository = final_exam_inscription_repository or FinalExamInscriptionRepository()
        self.student_repository = student_repository or StudentRepository()
        self.subject_repository = subject_repository or SubjectRepository()
        self.final_exam_repository = final_exam_repository or FinalExamRepository()
        self.grade_repository = grade_repository or GradeRepository()

    def inscribe_student_to_subject(self, student, subject):
        """
        Inscribe student to subject with grade creation.

        Business logic from subject_inscribe view.
        """
        try:
            with transaction.atomic():
                # Create or get inscription (from view logic)
                inscription, created = self.subject_inscription_repository.get_or_create(
                    student_id=student.id,
                    subject_code=subject.code
                )

                # Ensure grade record exists (from view logic)
                grade, grade_created = self.grade_repository.get_or_create(
                    student_id=student.id,
                    subject_code=subject.code
                )

                return {
                    'inscription': inscription,
                    'inscription_created': created,
                    'grade': grade,
                    'grade_created': grade_created
                }

        except Exception as e:
            raise InscriptionServiceError(f"Failed to inscribe student to subject: {str(e)}") from e

    def inscribe_student_to_final_exam(self, student, final_exam):
        """
        Inscribe student to final exam with eligibility validation.

        Business logic from final_exam_inscribe view.
        """
        try:
            with transaction.atomic():
                # Validate eligibility: student must have REGULAR status (from view logic)
                grade = self.grade_repository.list(
                    filters={'student': student, 'subject': final_exam.subject}
                    ).order_by('-id').first()

                if not grade or grade.status not in ['REGULAR']:  # Grade.StatusSubject.REGULAR
                    raise InscriptionServiceError("Solo puedes inscribirte si la materia está regular.")

                # Create or get inscription (from view logic)
                inscription, created = self.final_exam_inscription_repository.get_or_create(
                    student_id=student.id,
                    final_exam_id=final_exam.id
                )

                return {'inscription': inscription, 'created': created}

        except Exception as e:
            if isinstance(e, InscriptionServiceError):
                raise
            raise InscriptionServiceError(f"Failed to inscribe student to final exam: {str(e)}") from e

    def remove_subject_inscription(self, student_id, subject_code):
        """Remove subject inscription via repository."""
        try:
            with transaction.atomic():
                subject = self.subject_repository.by_code(subject_code)
                if not subject:
                    raise InscriptionServiceError(f"Subject {subject_code} not found")

                inscription = self.subject_inscription_repository.get_by_student_and_subject(student_id, subject.id)
                if not inscription:
                    raise InscriptionServiceError(
                        f"No inscription found for student {student_id} in subject {subject_code}"
                    )

                self.subject_inscription_repository.delete(inscription)
                return True

        except Exception as e:
            if isinstance(e, InscriptionServiceError):
                raise
            raise InscriptionServiceError(f"Failed to remove subject inscription: {str(e)}") from e

    def remove_final_exam_inscription(self, student_id, final_exam_id):
        """Remove final exam inscription via repository."""
        try:
            with transaction.atomic():
                inscription = self.final_exam_inscription_repository.get_by_student_and_final_exam(
                    student_id, final_exam_id
                )
                if not inscription:
                    raise InscriptionServiceError(
                        f"No inscription found for student {student_id} in final exam {final_exam_id}"
                    )

                self.final_exam_inscription_repository.delete(inscription)
                return True

        except Exception as e:
            if isinstance(e, InscriptionServiceError):
                raise
            raise InscriptionServiceError(f"Failed to remove final exam inscription: {str(e)}") from e
