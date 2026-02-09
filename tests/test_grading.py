"""Tests for grading app."""

from decimal import Decimal

import pytest
from django.urls import reverse

from enrollments.models import SubjectInscription
from exceptions import ServiceError
from grading.models import Grade
from grading.services import GradeService

pytestmark = pytest.mark.django_db


class TestGradeModel:
    """Test Grade model."""

    def test_create_grade(self, student, subject):
        """Test creating a grade."""
        grade = Grade.objects.create(
            student=student,
            subject=subject,
            status=Grade.StatusSubject.FREE,
        )
        assert grade.student == student
        assert grade.subject == subject
        assert grade.status == Grade.StatusSubject.FREE

    def test_grade_unique_together(self, student, subject):
        """Test that student-subject must be unique."""
        Grade.objects.create(student=student, subject=subject)
        with pytest.raises(Exception):
            Grade.objects.create(student=student, subject=subject)

    def test_grade_str(self, student, subject):
        """Test grade string representation."""
        grade = Grade.objects.create(student=student, subject=subject)
        assert student.user.username in str(grade)
        assert subject.name in str(grade)

    def test_update_status_promoted(self, grade):
        """Test status update to promoted when grade >= 6.0."""
        grade.final_grade = Decimal("7.5")
        grade.update_status()
        assert grade.status == Grade.StatusSubject.PROMOTED

    def test_update_status_regular(self, grade):
        """Test status update to regular when grade < 6.0."""
        grade.final_grade = Decimal("4.5")
        grade.update_status()
        assert grade.status == Grade.StatusSubject.REGULAR

    def test_update_status_free(self, grade):
        """Test status update to free when no final grade."""
        grade.final_grade = None
        grade.update_status()
        assert grade.status == Grade.StatusSubject.FREE

    def test_update_status_edge_case_six(self, grade):
        """Test status update when grade is exactly 6.0."""
        grade.final_grade = Decimal("6.0")
        grade.update_status()
        assert grade.status == Grade.StatusSubject.PROMOTED


class TestGradeService:
    """Test GradeService."""

    def test_get_subject_grades_with_backfill(
        self, subject, student, student2, professor
    ):
        """Test getting grades with backfill for missing students."""
        # Create inscriptions for both students
        SubjectInscription.objects.create(student=student, subject=subject)
        SubjectInscription.objects.create(student=student2, subject=subject)

        # Create grade for only one student
        Grade.objects.create(student=student, subject=subject)

        # Get grades with backfill
        grades = GradeService.get_subject_grades_with_backfill(subject, professor)

        # Should return grades for both students
        assert grades.count() == 2
        student_ids = [g.student_id for g in grades]
        assert student.student_id in student_ids
        assert student2.student_id in student_ids

    def test_get_subject_grades_no_backfill_needed(self, subject, student, professor):
        """Test getting grades when no backfill is needed."""
        SubjectInscription.objects.create(student=student, subject=subject)
        Grade.objects.create(student=student, subject=subject)

        grades = GradeService.get_subject_grades_with_backfill(subject, professor)

        assert grades.count() == 1
        assert grades.first().student == student

    def test_update_grade_promotion_only(self, grade):
        """Test updating only promotion grade."""
        updated = GradeService.update_grade(grade, promotion_grade=Decimal("8.0"))

        assert updated.promotion_grade == Decimal("8.0")
        assert updated.final_grade is None

    def test_update_grade_final_only(self, grade):
        """Test updating only final grade."""
        updated = GradeService.update_grade(grade, final_grade=Decimal("7.0"))

        assert updated.final_grade == Decimal("7.0")
        assert updated.status == Grade.StatusSubject.PROMOTED

    def test_update_grade_both(self, grade):
        """Test updating both grades."""
        updated = GradeService.update_grade(
            grade, promotion_grade=Decimal("8.0"), final_grade=Decimal("7.5")
        )

        assert updated.promotion_grade == Decimal("8.0")
        assert updated.final_grade == Decimal("7.5")
        assert updated.status == Grade.StatusSubject.PROMOTED

    def test_update_grade_auto_updates_status(self, grade):
        """Test that updating grade auto-updates status."""
        # Set to promoted
        GradeService.update_grade(grade, final_grade=Decimal("7.0"))
        assert grade.status == Grade.StatusSubject.PROMOTED

        # Change to regular
        GradeService.update_grade(grade, final_grade=Decimal("4.0"))
        grade.refresh_from_db()
        assert grade.status == Grade.StatusSubject.REGULAR

    def test_validate_grade_edit_permissions_success(
        self, grade, professor, subject, subject_inscription
    ):
        """Test successful permission validation."""
        # Assign professor to subject
        subject.professors.add(professor)

        # Should not raise exception
        result = GradeService.validate_grade_edit_permissions(grade, professor)
        assert result is True

    def test_validate_grade_edit_permissions_not_assigned(self, grade, professor):
        """Test validation fails when professor not assigned."""
        with pytest.raises(ServiceError) as exc_info:
            GradeService.validate_grade_edit_permissions(grade, professor)
        assert "no asignadas" in str(exc_info.value).lower()

    def test_validate_grade_edit_permissions_student_not_enrolled(
        self, grade, professor, subject
    ):
        """Test validation fails when student not enrolled."""
        # Assign professor to subject
        subject.professors.add(professor)

        with pytest.raises(ServiceError) as exc_info:
            GradeService.validate_grade_edit_permissions(grade, professor)
        assert "inscriptos" in str(exc_info.value).lower()


class TestGradingViews:
    """Test grading views."""

    def test_subject_grade_list_requires_professor(self, client, student_user, subject):
        """Test subject grade list requires professor role."""
        client.force_login(student_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )
        assert response.status_code == 403  # Permission denied

    def test_subject_grade_list_requires_assignment(
        self, client, professor_user, subject
    ):
        """Test professor must be assigned to subject."""
        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )
        # Should return 404 when professor not assigned (get_object_or_404 behavior)
        assert response.status_code == 404

    def test_subject_grade_list_success(
        self, client, professor_user, subject, student, subject_inscription
    ):
        """Test subject grade list for assigned professor."""
        # Assign professor to subject
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )
        assert response.status_code == 200
        assert "grades" in response.context
        assert "subject" in response.context

    def test_subject_grade_list_backfills_missing_grades(
        self, client, professor_user, subject, student, student2
    ):
        """Test that viewing grades backfills missing grade records."""
        # Create inscriptions
        SubjectInscription.objects.create(student=student, subject=subject)
        SubjectInscription.objects.create(student=student2, subject=subject)

        # Assign professor
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )

        assert response.status_code == 200
        # Both students should have grades now
        assert Grade.objects.filter(subject=subject).count() == 2

    def test_grade_update_get(
        self, client, professor_user, subject, grade, subject_inscription
    ):
        """Test grade update GET."""
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(reverse("grading:grade-edit", kwargs={"pk": grade.pk}))
        assert response.status_code == 200
        assert "form" in response.context
        assert "grade" in response.context

    def test_grade_update_post_success(
        self, client, professor_user, subject, grade, subject_inscription
    ):
        """Test successful grade update POST."""
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        data = {
            "promotion_grade": "8.5",
            "final_grade": "7.0",
            "notes": "Good work",
        }
        response = client.post(
            reverse("grading:grade-edit", kwargs={"pk": grade.pk}), data
        )
        assert response.status_code == 302  # Redirect on success

        grade.refresh_from_db()
        assert grade.promotion_grade == Decimal("8.5")
        assert grade.final_grade == Decimal("7.0")
        assert grade.status == Grade.StatusSubject.PROMOTED
        assert grade.notes == "Good work"

    def test_grade_update_not_assigned_fails(
        self, client, professor_user, grade, subject_inscription
    ):
        """Test grade update fails when professor not assigned."""
        client.force_login(professor_user)
        data = {"final_grade": "7.0"}
        response = client.post(
            reverse("grading:grade-edit", kwargs={"pk": grade.pk}), data
        )
        # Should redirect or show error
        assert response.status_code in [302, 200]

    def test_final_exam_inscriptions_list(
        self, client, professor_user, final_exam, student, subject_inscription
    ):
        """Test viewing final exam inscriptions."""
        from enrollments.models import FinalExamInscription

        # Assign professor to final
        final_exam.professors.add(professor_user.professor)

        # Create inscription
        FinalExamInscription.objects.create(student=student, final_exam=final_exam)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:final-inscriptions", kwargs={"pk": final_exam.pk})
        )
        assert response.status_code == 200
        assert "final_exam" in response.context
        assert "inscriptions" in response.context

    def test_final_exam_inscriptions_requires_assignment(
        self, client, professor_user, final_exam
    ):
        """Test final exam inscriptions requires professor assignment."""
        client.force_login(professor_user)
        response = client.get(
            reverse("grading:final-inscriptions", kwargs={"pk": final_exam.pk})
        )
        assert response.status_code == 302  # Redirect (not assigned)

    def test_subject_grade_list_success(
        self, client, professor_user, subject, student, subject_inscription
    ):
        """Test subject grade list for assigned professor."""
        # Assign professor to subject
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )
        assert response.status_code == 200
        assert "grades" in response.context
        assert "subject" in response.context

    def test_subject_grade_list_backfills_missing_grades(
        self, client, professor_user, subject, student, student2
    ):
        """Test that viewing grades backfills missing grade records."""
        # Create inscriptions
        SubjectInscription.objects.create(student=student, subject=subject)
        SubjectInscription.objects.create(student=student2, subject=subject)

        # Assign professor
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )

        assert response.status_code == 200
        # Both students should have grades now
        assert Grade.objects.filter(subject=subject).count() == 2

    def test_grade_update_get(
        self, client, professor_user, subject, grade, subject_inscription
    ):
        """Test grade update GET."""
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(reverse("grading:grade-edit", kwargs={"pk": grade.pk}))
        assert response.status_code == 200
        assert "form" in response.context
        assert "grade" in response.context

    def test_grade_update_post_success(
        self, client, professor_user, subject, grade, subject_inscription
    ):
        """Test successful grade update POST."""
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        data = {
            "promotion_grade": "8.5",
            "final_grade": "7.0",
            "notes": "Good work",
        }
        response = client.post(
            reverse("grading:grade-edit", kwargs={"pk": grade.pk}), data
        )
        assert response.status_code == 302  # Redirect on success

        grade.refresh_from_db()
        assert grade.promotion_grade == Decimal("8.5")
        assert grade.final_grade == Decimal("7.0")
        assert grade.status == Grade.StatusSubject.PROMOTED
        assert grade.notes == "Good work"

    def test_grade_update_not_assigned_fails(
        self, client, professor_user, grade, subject_inscription
    ):
        """Test grade update fails when professor not assigned."""
        client.force_login(professor_user)
        data = {"final_grade": "7.0"}
        response = client.post(
            reverse("grading:grade-edit", kwargs={"pk": grade.pk}), data
        )
        # Should redirect or show error
        assert response.status_code in [302, 200]

    def test_final_exam_inscriptions_list(
        self, client, professor_user, final_exam, student, subject_inscription
    ):
        """Test viewing final exam inscriptions."""
        from enrollments.models import FinalExamInscription

        # Assign professor to final
        final_exam.professors.add(professor_user.professor)

        # Create inscription
        FinalExamInscription.objects.create(student=student, final_exam=final_exam)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:final-inscriptions", kwargs={"pk": final_exam.pk})
        )
        assert response.status_code == 200
        assert "final_exam" in response.context
        assert "inscriptions" in response.context

    def test_final_exam_inscriptions_requires_assignment(
        self, client, professor_user, final_exam
    ):
        """Test final exam inscriptions requires professor assignment."""
        client.force_login(professor_user)
        response = client.get(
            reverse("grading:final-inscriptions", kwargs={"pk": final_exam.pk})
        )
        assert response.status_code == 302  # Redirect (not assigned)

    def test_subject_grade_list_success(
        self, client, professor_user, subject, student, subject_inscription
    ):
        """Test subject grade list for assigned professor."""
        # Assign professor to subject
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )
        assert response.status_code == 200
        assert "grades" in response.context
        assert "subject" in response.context

    def test_subject_grade_list_backfills_missing_grades(
        self, client, professor_user, subject, student, student2
    ):
        """Test that viewing grades backfills missing grade records."""
        # Create inscriptions
        SubjectInscription.objects.create(student=student, subject=subject)
        SubjectInscription.objects.create(student=student2, subject=subject)

        # Assign professor
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:subject-grades", kwargs={"code": subject.code})
        )

        assert response.status_code == 200
        # Both students should have grades now
        assert Grade.objects.filter(subject=subject).count() == 2

    def test_grade_update_get(
        self, client, professor_user, subject, grade, subject_inscription
    ):
        """Test grade update GET."""
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        response = client.get(reverse("grading:grade-edit", kwargs={"pk": grade.pk}))
        assert response.status_code == 200
        assert "form" in response.context
        assert "object" in response.context  # UpdateView uses 'object' by default

    def test_grade_update_post_success(
        self, client, professor_user, subject, grade, subject_inscription
    ):
        """Test successful grade update POST."""
        subject.professors.add(professor_user.professor)

        client.force_login(professor_user)
        data = {
            "promotion_grade": "8.5",
            "final_grade": "7.0",
            "notes": "Good work",
        }
        response = client.post(
            reverse("grading:grade-edit", kwargs={"pk": grade.pk}), data
        )
        assert response.status_code == 302  # Redirect on success

        grade.refresh_from_db()
        assert grade.promotion_grade == Decimal("8.5")
        assert grade.final_grade == Decimal("7.0")
        assert grade.status == Grade.StatusSubject.PROMOTED
        assert grade.notes == "Good work"

    def test_grade_update_not_assigned_fails(
        self, client, professor_user, grade, subject_inscription
    ):
        """Test grade update fails when professor not assigned."""
        client.force_login(professor_user)
        data = {"final_grade": "7.0"}
        response = client.post(
            reverse("grading:grade-edit", kwargs={"pk": grade.pk}), data
        )
        # Should return 404 when professor not assigned (get_object_or_404 behavior)
        assert response.status_code == 404

    def test_final_exam_inscriptions_list(
        self, client, professor_user, final_exam, student, subject_inscription
    ):
        """Test viewing final exam inscriptions."""
        from enrollments.models import FinalExamInscription

        # Assign professor to final
        final_exam.professors.add(professor_user.professor)

        # Create inscription
        FinalExamInscription.objects.create(student=student, final_exam=final_exam)

        client.force_login(professor_user)
        response = client.get(
            reverse("grading:final-inscriptions", kwargs={"pk": final_exam.pk})
        )
        assert response.status_code == 200
        assert "final" in response.context  # View uses 'final' not 'final_exam'
        assert "inscriptions" in response.context

    def test_final_exam_inscriptions_requires_assignment(
        self, client, professor_user, final_exam
    ):
        """Test final exam inscriptions requires professor assignment."""
        client.force_login(professor_user)
        response = client.get(
            reverse("grading:final-inscriptions", kwargs={"pk": final_exam.pk})
        )
        # Should return 404 when professor not assigned (get_object_or_404 behavior)
        assert response.status_code == 404


class TestGradeStatusTransitions:
    """Test grade status transitions."""

    def test_free_to_regular(self, grade):
        """Test transition from FREE to REGULAR."""
        assert grade.status == Grade.StatusSubject.FREE

        grade.final_grade = Decimal("4.0")
        grade.update_status()

        assert grade.status == Grade.StatusSubject.REGULAR

    def test_free_to_promoted(self, grade):
        """Test transition from FREE to PROMOTED."""
        assert grade.status == Grade.StatusSubject.FREE

        grade.final_grade = Decimal("7.0")
        grade.update_status()

        assert grade.status == Grade.StatusSubject.PROMOTED

    def test_regular_to_promoted(self, grade):
        """Test transition from REGULAR to PROMOTED."""
        grade.final_grade = Decimal("4.0")
        grade.update_status()
        assert grade.status == Grade.StatusSubject.REGULAR

        grade.final_grade = Decimal("8.0")
        grade.update_status()

        assert grade.status == Grade.StatusSubject.PROMOTED

    def test_promoted_to_regular(self, grade):
        """Test transition from PROMOTED to REGULAR."""
        grade.final_grade = Decimal("7.0")
        grade.update_status()
        assert grade.status == Grade.StatusSubject.PROMOTED

        grade.final_grade = Decimal("3.0")
        grade.update_status()

        assert grade.status == Grade.StatusSubject.REGULAR

    def test_any_to_free(self, grade):
        """Test transition to FREE when final_grade is None."""
        grade.final_grade = Decimal("7.0")
        grade.update_status()
        assert grade.status == Grade.StatusSubject.PROMOTED

        grade.final_grade = None
        grade.update_status()

        assert grade.status == Grade.StatusSubject.FREE
