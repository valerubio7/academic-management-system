"""Tests for enrollments app."""

from datetime import date, timedelta

import pytest
from django.urls import reverse

from enrollments.models import FinalExam, FinalExamInscription, SubjectInscription
from enrollments.services import EnrollmentService
from exceptions import ServiceError
from grading.models import Grade

pytestmark = pytest.mark.django_db


class TestFinalExamModel:
    """Test FinalExam model."""

    def test_create_final_exam(self, subject):
        """Test creating a final exam."""
        final = FinalExam.objects.create(
            subject=subject,
            date=date.today() + timedelta(days=30),
            location="Room 101",
            duration=timedelta(hours=2),
            call_number=1,
            notes="First call",
        )
        assert final.subject == subject
        assert final.call_number == 1
        assert "Final Exam" in str(final)

    def test_final_exam_str(self, subject):
        """Test final exam string representation."""
        final = FinalExam.objects.create(
            subject=subject,
            date=date(2024, 6, 15),
            location="Room 101",
            duration=timedelta(hours=2),
            call_number=1,
        )
        assert subject.name in str(final)
        assert "2024-06-15" in str(final)


class TestSubjectInscriptionModel:
    """Test SubjectInscription model."""

    def test_create_subject_inscription(self, student, subject):
        """Test creating a subject inscription."""
        inscription = SubjectInscription.objects.create(
            student=student, subject=subject
        )
        assert inscription.student == student
        assert inscription.subject == subject
        assert inscription.inscription_date is not None

    def test_subject_inscription_unique_together(self, student, subject):
        """Test that student-subject must be unique."""
        SubjectInscription.objects.create(student=student, subject=subject)
        with pytest.raises(Exception):
            SubjectInscription.objects.create(student=student, subject=subject)

    def test_subject_inscription_str(self, student, subject):
        """Test subject inscription string representation."""
        inscription = SubjectInscription.objects.create(
            student=student, subject=subject
        )
        assert student.user.username in str(inscription)
        assert subject.name in str(inscription)


class TestFinalExamInscriptionModel:
    """Test FinalExamInscription model."""

    def test_create_final_exam_inscription(self, student, final_exam):
        """Test creating a final exam inscription."""
        inscription = FinalExamInscription.objects.create(
            student=student, final_exam=final_exam
        )
        assert inscription.student == student
        assert inscription.final_exam == final_exam
        assert inscription.inscription_date is not None

    def test_final_exam_inscription_unique_together(self, student, final_exam):
        """Test that student-final_exam must be unique."""
        FinalExamInscription.objects.create(student=student, final_exam=final_exam)
        with pytest.raises(Exception):
            FinalExamInscription.objects.create(student=student, final_exam=final_exam)

    def test_final_exam_inscription_str(self, student, final_exam):
        """Test final exam inscription string representation."""
        inscription = FinalExamInscription.objects.create(
            student=student, final_exam=final_exam
        )
        assert student.user.username in str(inscription)
        assert final_exam.subject.name in str(inscription)


class TestEnrollmentService:
    """Test EnrollmentService."""

    def test_can_enroll_in_subject_success(self, student, subject):
        """Test successful enrollment validation."""
        can_enroll, reason = EnrollmentService.can_enroll_in_subject(student, subject)
        assert can_enroll is True
        assert reason == ""

    def test_can_enroll_in_subject_wrong_career(self, student, subject2, faculty):
        """Test enrollment fails for wrong career."""
        from academics.models import Career, Subject

        # Create a different career
        other_career = Career.objects.create(
            code="OTHER",
            name="Other Career",
            faculty=faculty,
            director="Dr. Other",
            duration_years=4,
        )
        other_subject = Subject.objects.create(
            code="OTHER01",
            name="Other Subject",
            career=other_career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=4,
        )
        can_enroll, reason = EnrollmentService.can_enroll_in_subject(
            student, other_subject
        )
        assert can_enroll is False
        assert "does not belong to your career" in reason

    def test_can_enroll_in_subject_already_enrolled(
        self, student, subject, subject_inscription
    ):
        """Test enrollment fails when already enrolled."""
        can_enroll, reason = EnrollmentService.can_enroll_in_subject(student, subject)
        assert can_enroll is False
        assert "Already enrolled" in reason

    def test_enroll_in_subject_success(self, student, subject):
        """Test successful subject enrollment."""
        inscription = EnrollmentService.enroll_in_subject(student, subject)
        assert inscription.student == student
        assert inscription.subject == subject
        # Check that grade was created
        assert Grade.objects.filter(student=student, subject=subject).exists()

    def test_enroll_in_subject_creates_grade(self, student, subject):
        """Test that enrollment creates a grade record."""
        EnrollmentService.enroll_in_subject(student, subject)
        grade = Grade.objects.get(student=student, subject=subject)
        assert grade.status == Grade.StatusSubject.FREE

    def test_enroll_in_subject_already_enrolled_raises(
        self, student, subject, subject_inscription
    ):
        """Test that enrolling twice raises error."""
        with pytest.raises(ServiceError):
            EnrollmentService.enroll_in_subject(student, subject)

    def test_can_enroll_in_final_success(
        self, student, subject, final_exam, subject_inscription
    ):
        """Test successful final exam enrollment validation."""
        can_enroll, reason = EnrollmentService.can_enroll_in_final(student, final_exam)
        assert can_enroll is True
        assert reason == ""

    def test_can_enroll_in_final_not_enrolled_in_subject(self, student, final_exam):
        """Test final enrollment fails when not enrolled in subject."""
        can_enroll, reason = EnrollmentService.can_enroll_in_final(student, final_exam)
        assert can_enroll is False
        assert "must be enrolled in the subject first" in reason

    def test_can_enroll_in_final_already_enrolled(
        self, student, final_exam, subject_inscription, final_exam_inscription
    ):
        """Test final enrollment fails when already enrolled."""
        can_enroll, reason = EnrollmentService.can_enroll_in_final(student, final_exam)
        assert can_enroll is False
        assert "Already enrolled in this final exam" in reason

    def test_can_enroll_in_final_already_promoted(
        self, student, subject, final_exam, subject_inscription, grade
    ):
        """Test final enrollment fails when already promoted."""
        grade.final_grade = 7.0
        grade.update_status()
        can_enroll, reason = EnrollmentService.can_enroll_in_final(student, final_exam)
        assert can_enroll is False
        assert "already passed this subject" in reason

    def test_enroll_in_final_success(self, student, final_exam, subject_inscription):
        """Test successful final exam enrollment."""
        inscription = EnrollmentService.enroll_in_final(student, final_exam)
        assert inscription.student == student
        assert inscription.final_exam == final_exam

    def test_enroll_in_final_not_enrolled_raises(self, student, final_exam):
        """Test that enrolling in final without subject enrollment raises error."""
        with pytest.raises(ServiceError):
            EnrollmentService.enroll_in_final(student, final_exam)

    def test_get_available_subjects_for_student(self, student, subject, subject2):
        """Test getting available subjects for student."""
        # Enroll in subject1
        SubjectInscription.objects.create(student=student, subject=subject)
        # Only subject2 should be available
        available = EnrollmentService.get_available_subjects_for_student(student)
        assert subject2 in available
        assert subject not in available

    def test_get_available_subjects_no_career(self, student_user):
        """Test getting available subjects when student has no career."""
        student_user.student.career = None
        student_user.student.save()
        available = EnrollmentService.get_available_subjects_for_student(
            student_user.student
        )
        assert available.count() == 0

    def test_get_available_finals_for_student(
        self, student, subject, final_exam, subject_inscription
    ):
        """Test getting available finals for student."""
        available = EnrollmentService.get_available_finals_for_student(student)
        assert final_exam in available

    def test_get_available_finals_excludes_enrolled(
        self, student, final_exam, subject_inscription, final_exam_inscription
    ):
        """Test that already enrolled finals are excluded."""
        available = EnrollmentService.get_available_finals_for_student(student)
        assert final_exam not in available

    def test_get_available_finals_excludes_promoted(
        self, student, subject, final_exam, subject_inscription, grade
    ):
        """Test that finals for promoted subjects are excluded."""
        grade.final_grade = 8.0
        grade.update_status()
        available = EnrollmentService.get_available_finals_for_student(student)
        assert final_exam not in available


class TestEnrollmentViews:
    """Test enrollment views."""

    def test_available_subjects_requires_student(self, client, admin_user):
        """Test available subjects requires student role."""
        client.force_login(admin_user)
        response = client.get(reverse("enrollments:available-subjects"))
        assert response.status_code == 403  # Permission denied

    def test_final_enroll_get(
        self, client, student_user, final_exam, subject_inscription
    ):
        """Test final exam enrollment confirmation GET."""
        client.force_login(student_user)
        response = client.get(
            reverse("enrollments:final-enroll", kwargs={"pk": final_exam.pk})
        )
        assert response.status_code == 200
        assert "final" in response.context  # View uses 'final' not 'final_exam'

    def test_final_exam_list_requires_admin(self, client, student_user):
        """Test final exam list requires admin."""
        client.force_login(student_user)
        response = client.get(reverse("enrollments:final-list"))
        assert response.status_code == 403  # Permission denied

    def test_final_exam_list_success(self, client, admin_user, final_exam):
        """Test final exam list for admin."""
        client.force_login(admin_user)
        response = client.get(reverse("enrollments:final-list"))
        assert response.status_code == 200
        assert "finals" in response.context  # View uses 'finals' not 'final_exams'

    def test_final_exam_create_post(self, client, admin_user, subject):
        """Test creating a final exam."""
        client.force_login(admin_user)
        data = {
            "subject": subject.code,
            "date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "location": "Room 202",
            "duration": "02:00:00",
            "call_number": 2,
            "notes": "Second call",
        }
        response = client.post(reverse("enrollments:final-create"), data)
        assert response.status_code == 302
        assert FinalExam.objects.filter(call_number=2).exists()

    def test_assign_professors_to_final(
        self, client, admin_user, final_exam, professor
    ):
        """Test assigning professors to final exam."""
        client.force_login(admin_user)
        data = {"professors": [professor.professor_id]}
        response = client.post(
            reverse(
                "enrollments:final-assign-professors", kwargs={"pk": final_exam.pk}
            ),
            data,
        )
        assert response.status_code == 302
        assert professor in final_exam.professors.all()
