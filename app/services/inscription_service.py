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

    def inscribe_student_to_subject(self, student_id, subject_code, validate_eligibility=True):
        """
        Inscribe student to subject.

        Business rules:
        - Student must exist
        - Subject must exist and belong to student's career
        - No duplicate inscriptions
        """
        try:
            with transaction.atomic():
                # Get student and subject via repositories
                student = self.student_repository.get_by_id(student_id)
                if not student:
                    raise InscriptionServiceError(f"Student {student_id} not found")

                subject = self.subject_repository.by_code(subject_code)
                if not subject:
                    raise InscriptionServiceError(f"Subject {subject_code} not found")

                # Validate career match if requested
                if validate_eligibility and subject.career != student.career:
                    raise InscriptionServiceError(f"Subject {subject_code} does not belong to student's career")

                # Check for duplicate
                existing = self.subject_inscription_repository.get_by_student_and_subject(student_id, subject.id)
                if existing:
                    raise InscriptionServiceError(f"Student already inscribed to subject {subject_code}")

                # Create inscription via repository
                inscription_data = {'student': student, 'subject': subject}
                return self.subject_inscription_repository.create(inscription_data)

        except Exception as e:
            if isinstance(e, InscriptionServiceError):
                raise
            raise InscriptionServiceError(f"Failed to inscribe student to subject: {str(e)}") from e

    def inscribe_student_to_final_exam(self, student_id, final_exam_id, validate_eligibility=True):
        """
        Inscribe student to final exam.

        Business rules:
        - Student must exist
        - Final exam must exist and belong to student's career
        - No duplicate inscriptions
        """
        try:
            with transaction.atomic():
                # Get student and final exam via repositories
                student = self.student_repository.get_by_id(student_id)
                if not student:
                    raise InscriptionServiceError(f"Student {student_id} not found")

                final_exam = self.final_exam_repository.get_by_id(final_exam_id)
                if not final_exam:
                    raise InscriptionServiceError(f"Final exam {final_exam_id} not found")

                # Validate career match if requested
                if validate_eligibility and final_exam.subject.career != student.career:
                    raise InscriptionServiceError("Final exam does not belong to student's career")

                # Check for duplicate
                existing = self.final_exam_inscription_repository.get_by_student_and_final_exam(
                    student_id, final_exam_id
                )
                if existing:
                    raise InscriptionServiceError("Student already inscribed to this final exam")

                # Create inscription via repository
                inscription_data = {'student': student, 'final_exam': final_exam}
                return self.final_exam_inscription_repository.create(inscription_data)

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
                        f"No inscription found for student {student_id} in subject {subject_code}")

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
