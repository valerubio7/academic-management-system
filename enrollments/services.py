from django.db import transaction
from django.db.models import Q

from academics.models import Subject
from exceptions import ServiceError
from enrollments.models import FinalExam, FinalExamInscription, SubjectInscription
from grading.models import Grade
from users.models import Student


class EnrollmentService:
    """Handles enrollment business rules and validations."""

    @staticmethod
    def _validate_enrollment(can_enroll_func, *args, service_name):
        """Generic validation helper for enrollment operations."""
        can_enroll, reason = can_enroll_func(*args)
        if not can_enroll:
            raise ServiceError("EnrollmentService", service_name, reason)

    @staticmethod
    def can_enroll_in_subject(student: Student, subject: Subject) -> tuple[bool, str]:
        if subject.career != student.career:
            return False, "Subject does not belong to your career"

        if SubjectInscription.objects.filter(student=student, subject=subject).exists():
            return False, "Already enrolled in this subject"

        return True, ""

    @staticmethod
    @transaction.atomic
    def enroll_in_subject(student: Student, subject: Subject) -> SubjectInscription:
        try:
            EnrollmentService._validate_enrollment(
                EnrollmentService.can_enroll_in_subject,
                student,
                subject,
                service_name="enroll_in_subject",
            )

            inscription = SubjectInscription.objects.create(
                student=student, subject=subject
            )

            Grade.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={"status": Grade.StatusSubject.FREE},
            )

            return inscription

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError("EnrollmentService", "enroll_in_subject", str(e), e)

    @staticmethod
    def can_enroll_in_final(
        student: Student, final_exam: FinalExam
    ) -> tuple[bool, str]:
        if not SubjectInscription.objects.filter(
            student=student, subject=final_exam.subject
        ).exists():
            return False, "You must be enrolled in the subject first"

        if FinalExamInscription.objects.filter(
            student=student, final_exam=final_exam
        ).exists():
            return False, "Already enrolled in this final exam"

        try:
            grade = Grade.objects.get(student=student, subject=final_exam.subject)
            if grade.status == Grade.StatusSubject.PROMOTED:
                return False, "You already passed this subject"
        except Grade.DoesNotExist:
            pass

        return True, ""

    @staticmethod
    @transaction.atomic
    def enroll_in_final(
        student: Student, final_exam: FinalExam
    ) -> FinalExamInscription:
        try:
            EnrollmentService._validate_enrollment(
                EnrollmentService.can_enroll_in_final,
                student,
                final_exam,
                service_name="enroll_in_final",
            )

            inscription = FinalExamInscription.objects.create(
                student=student, final_exam=final_exam
            )

            return inscription

        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError("EnrollmentService", "enroll_in_final", str(e), e)

    @staticmethod
    def get_available_subjects_for_student(student: Student):
        if not student.career:
            return Subject.objects.none()

        enrolled_subjects = SubjectInscription.objects.filter(
            student=student
        ).values_list("subject_id", flat=True)

        return (
            Subject.objects.filter(career=student.career)
            .exclude(code__in=enrolled_subjects)
            .select_related("career__faculty")
        )

    @staticmethod
    def get_available_finals_for_student(student: Student):
        enrolled_subjects = SubjectInscription.objects.filter(
            student=student
        ).values_list("subject_id", flat=True)

        enrolled_finals = FinalExamInscription.objects.filter(
            student=student
        ).values_list("final_exam_id", flat=True)

        promoted_subjects = Grade.objects.filter(
            student=student, status=Grade.StatusSubject.PROMOTED
        ).values_list("subject_id", flat=True)

        return (
            FinalExam.objects.filter(subject_id__in=enrolled_subjects)
            .exclude(id__in=enrolled_finals)
            .exclude(subject_id__in=promoted_subjects)
            .select_related("subject__career")
        )
