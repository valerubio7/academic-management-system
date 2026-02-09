"""Tests for academics app."""

from datetime import date

import pytest
from django.urls import reverse

from academics.models import Career, Faculty, Subject

pytestmark = pytest.mark.django_db


class TestFacultyModel:
    """Test Faculty model."""

    def test_create_faculty(self):
        """Test creating a faculty."""
        faculty = Faculty.objects.create(
            code="TEST",
            name="Test Faculty",
            address="123 Test St",
            phone="+1234567890",
            email="test@faculty.com",
            website="https://test.faculty.com",
            dean="Dr. Test",
            established_date=date(2000, 1, 1),
            description="Test description",
        )
        assert faculty.code == "TEST"
        assert faculty.name == "Test Faculty"
        assert str(faculty) == "Test Faculty"

    def test_faculty_code_is_primary_key(self):
        """Test that code is the primary key."""
        faculty = Faculty.objects.create(
            code="PK1",
            name="Faculty 1",
            address="Address",
            phone="123",
            email="test@test.com",
            website="http://test.com",
            dean="Dean",
            established_date=date.today(),
        )
        assert faculty.pk == "PK1"


class TestCareerModel:
    """Test Career model."""

    def test_create_career(self, faculty):
        """Test creating a career."""
        career = Career.objects.create(
            code="TEST",
            name="Test Career",
            faculty=faculty,
            director="Dr. Director",
            duration_years=5,
            description="Test career description",
        )
        assert career.code == "TEST"
        assert career.name == "Test Career"
        assert career.faculty == faculty

    def test_career_str(self, faculty):
        """Test career string representation."""
        career = Career.objects.create(
            code="CS",
            name="Computer Science",
            faculty=faculty,
            director="Dr. CS",
            duration_years=5,
        )
        assert "Computer Science" in str(career)
        assert "(CS)" in str(career)
        assert faculty.name in str(career)

    def test_career_cascade_delete(self, faculty):
        """Test that deleting faculty cascades to careers."""
        career = Career.objects.create(
            code="TEST",
            name="Test",
            faculty=faculty,
            director="Dr.",
            duration_years=5,
        )
        faculty.delete()
        assert not Career.objects.filter(code="TEST").exists()


class TestSubjectModel:
    """Test Subject model."""

    def test_create_subject(self, career):
        """Test creating a subject."""
        subject = Subject.objects.create(
            code="SUB01",
            name="Test Subject",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=6,
            description="Test subject",
        )
        assert subject.code == "SUB01"
        assert subject.name == "Test Subject"
        assert subject.career == career

    def test_subject_str(self, career):
        """Test subject string representation."""
        subject = Subject.objects.create(
            code="MATH1",
            name="Mathematics 1",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.ANNUAL,
            semanal_hours=4,
        )
        assert "Mathematics 1" in str(subject)
        assert "(MATH1)" in str(subject)
        assert career.name in str(subject)

    def test_subject_categories(self, career):
        """Test subject category choices."""
        obligatory = Subject.objects.create(
            code="OBL1",
            name="Obligatory Subject",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=4,
        )
        elective = Subject.objects.create(
            code="ELEC1",
            name="Elective Subject",
            career=career,
            year=2,
            category=Subject.Category.ELECTIVE,
            period=Subject.Period.SECOND,
            semanal_hours=4,
        )
        assert obligatory.category == Subject.Category.OBLIGATORY
        assert elective.category == Subject.Category.ELECTIVE

    def test_subject_periods(self, career):
        """Test subject period choices."""
        first = Subject.objects.create(
            code="FIRST",
            name="First Period",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=4,
        )
        second = Subject.objects.create(
            code="SECOND",
            name="Second Period",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.SECOND,
            semanal_hours=4,
        )
        annual = Subject.objects.create(
            code="ANNUAL",
            name="Annual",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.ANNUAL,
            semanal_hours=8,
        )
        assert first.period == Subject.Period.FIRST
        assert second.period == Subject.Period.SECOND
        assert annual.period == Subject.Period.ANNUAL

    def test_subject_cascade_delete(self, career):
        """Test that deleting career cascades to subjects."""
        subject = Subject.objects.create(
            code="TEST",
            name="Test",
            career=career,
            year=1,
            category=Subject.Category.OBLIGATORY,
            period=Subject.Period.FIRST,
            semanal_hours=4,
        )
        career.delete()
        assert not Subject.objects.filter(code="TEST").exists()


class TestAcademicsViews:
    """Test academics views."""

    def test_faculty_list_requires_admin(self, client, student_user):
        """Test faculty list requires admin role."""
        client.force_login(student_user)
        response = client.get(reverse("academics:faculty-list"))
        assert response.status_code == 403  # Permission denied

    def test_faculty_list_success(self, client, admin_user, faculty):
        """Test faculty list for admin."""
        client.force_login(admin_user)
        response = client.get(reverse("academics:faculty-list"))
        assert response.status_code == 200
        assert "faculties" in response.context

    def test_faculty_create_get(self, client, admin_user):
        """Test faculty create GET."""
        client.force_login(admin_user)
        response = client.get(reverse("academics:faculty-create"))
        assert response.status_code == 200
        assert "form" in response.context

    def test_faculty_create_post(self, client, admin_user):
        """Test faculty create POST."""
        client.force_login(admin_user)
        data = {
            "code": "NEW",
            "name": "New Faculty",
            "address": "123 New St",
            "phone": "+1234567890",
            "email": "new@faculty.com",
            "website": "https://new.faculty.com",
            "dean": "Dr. New",
            "established_date": "2020-01-01",
            "description": "New faculty",
        }
        response = client.post(reverse("academics:faculty-create"), data)
        assert response.status_code == 302  # Redirect on success
        assert Faculty.objects.filter(code="NEW").exists()

    def test_faculty_update_get(self, client, admin_user, faculty):
        """Test faculty update GET."""
        client.force_login(admin_user)
        response = client.get(
            reverse("academics:faculty-edit", kwargs={"code": faculty.code})
        )
        assert response.status_code == 200
        assert "form" in response.context

    def test_faculty_update_post(self, client, admin_user, faculty):
        """Test faculty update POST."""
        client.force_login(admin_user)
        data = {
            "code": faculty.code,
            "name": "Updated Faculty",
            "address": faculty.address,
            "phone": faculty.phone,
            "email": faculty.email,
            "website": faculty.website,
            "dean": faculty.dean,
            "established_date": faculty.established_date,
        }
        response = client.post(
            reverse("academics:faculty-edit", kwargs={"code": faculty.code}), data
        )
        assert response.status_code == 302
        faculty.refresh_from_db()
        assert faculty.name == "Updated Faculty"

    def test_faculty_delete(self, client, admin_user, faculty):
        """Test faculty delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("academics:faculty-delete", kwargs={"code": faculty.code})
        )
        assert response.status_code == 302
        assert not Faculty.objects.filter(code=faculty.code).exists()

    def test_career_list_success(self, client, admin_user, career):
        """Test career list."""
        client.force_login(admin_user)
        response = client.get(reverse("academics:career-list"))
        assert response.status_code == 200
        assert "careers" in response.context

    def test_career_create_post(self, client, admin_user, faculty):
        """Test career create POST."""
        client.force_login(admin_user)
        data = {
            "code": "NEWCAR",
            "name": "New Career",
            "faculty": faculty.code,
            "director": "Dr. Director",
            "duration_years": 4,
            "description": "New career",
        }
        response = client.post(reverse("academics:career-create"), data)
        assert response.status_code == 302
        assert Career.objects.filter(code="NEWCAR").exists()

    def test_career_update_post(self, client, admin_user, career):
        """Test career update POST."""
        client.force_login(admin_user)
        data = {
            "code": career.code,
            "name": "Updated Career",
            "faculty": career.faculty.code,
            "director": career.director,
            "duration_years": career.duration_years,
        }
        response = client.post(
            reverse("academics:career-edit", kwargs={"code": career.code}), data
        )
        assert response.status_code == 302
        career.refresh_from_db()
        assert career.name == "Updated Career"

    def test_career_delete(self, client, admin_user, career):
        """Test career delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("academics:career-delete", kwargs={"code": career.code})
        )
        assert response.status_code == 302
        assert not Career.objects.filter(code=career.code).exists()

    def test_subject_list_success(self, client, admin_user, subject):
        """Test subject list."""
        client.force_login(admin_user)
        response = client.get(reverse("academics:subject-list"))
        assert response.status_code == 200
        assert "subjects" in response.context

    def test_subject_create_post(self, client, admin_user, career):
        """Test subject create POST."""
        client.force_login(admin_user)
        data = {
            "code": "NEWSUB",
            "name": "New Subject",
            "career": career.code,
            "year": 1,
            "category": Subject.Category.OBLIGATORY,
            "period": Subject.Period.FIRST,
            "semanal_hours": 6,
            "description": "New subject",
        }
        response = client.post(reverse("academics:subject-create"), data)
        assert response.status_code == 302
        assert Subject.objects.filter(code="NEWSUB").exists()

    def test_subject_update_post(self, client, admin_user, subject):
        """Test subject update POST."""
        client.force_login(admin_user)
        data = {
            "code": subject.code,
            "name": "Updated Subject",
            "career": subject.career.code,
            "year": subject.year,
            "category": subject.category,
            "period": subject.period,
            "semanal_hours": subject.semanal_hours,
        }
        response = client.post(
            reverse("academics:subject-edit", kwargs={"code": subject.code}), data
        )
        assert response.status_code == 302
        subject.refresh_from_db()
        assert subject.name == "Updated Subject"

    def test_subject_delete(self, client, admin_user, subject):
        """Test subject delete."""
        client.force_login(admin_user)
        response = client.post(
            reverse("academics:subject-delete", kwargs={"code": subject.code})
        )
        assert response.status_code == 302
        assert not Subject.objects.filter(code=subject.code).exists()

    def test_assign_professors_to_subject(self, client, admin_user, subject, professor):
        """Test assigning professors to subject."""
        client.force_login(admin_user)
        data = {"professors": [professor.professor_id]}
        response = client.post(
            reverse(
                "academics:subject-assign-professors", kwargs={"code": subject.code}
            ),
            data,
        )
        assert response.status_code == 302
        assert professor in subject.professors.all()
