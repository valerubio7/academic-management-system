from django.db import transaction

from exceptions import ServiceError


class GradeService:
    @staticmethod
    @transaction.atomic
    def get_subject_grades_with_backfill(subject, professor):
        """Get grades for subject and create missing Grade entries for enrolled students."""
        from enrollments.models import SubjectInscription
        from grading.models import Grade

        try:
            enrolled_student_ids = set(
                SubjectInscription.objects.filter(subject=subject).values_list(
                    "student_id", flat=True
                )
            )

            existing_grade_student_ids = set(
                Grade.objects.filter(subject=subject).values_list(
                    "student_id", flat=True
                )
            )

            missing_ids = enrolled_student_ids - existing_grade_student_ids
            if missing_ids:
                Grade.objects.bulk_create(
                    [Grade(student_id=sid, subject=subject) for sid in missing_ids]
                )

            return (
                Grade.objects.filter(subject=subject)
                .select_related("student__user")
                .order_by("student__user__last_name", "student__user__first_name")
            )

        except Exception as e:
            raise ServiceError(
                service="GradeService",
                operation="get_subject_grades_with_backfill",
                message=f"Failed to get subject grades: {str(e)}",
                original_exception=e,
            )

    @staticmethod
    @transaction.atomic
    def update_grade(grade, promotion_grade=None, final_grade=None):
        """Update grade and automatically recalculate status."""
        try:
            if promotion_grade is not None:
                grade.promotion_grade = promotion_grade
            if final_grade is not None:
                grade.final_grade = final_grade

            grade.save()
            grade.update_status()

            return grade

        except Exception as e:
            raise ServiceError(
                service="GradeService",
                operation="update_grade",
                message=f"Failed to update grade: {str(e)}",
                original_exception=e,
            )

    @staticmethod
    def validate_grade_edit_permissions(grade, professor):
        """Validate professor can edit this grade."""
        from enrollments.models import SubjectInscription

        validations = [
            (
                grade.subject.professors.filter(pk=professor.pk).exists(),
                "No puede editar notas de materias no asignadas.",
            ),
            (
                SubjectInscription.objects.filter(
                    student=grade.student, subject=grade.subject
                ).exists(),
                "Solo puede calificar a estudiantes inscriptos en la materia.",
            ),
        ]

        for is_valid, error_message in validations:
            if not is_valid:
                raise ServiceError(
                    service="GradeService",
                    operation="validate_grade_edit_permissions",
                    message=error_message,
                )

        return True
