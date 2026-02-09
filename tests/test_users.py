"""Tests for users app."""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from exceptions import ServiceError
from users.models import Administrator, Professor, Student
from users.services import AssignmentService, UserService

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestCustomUserModel:
    """Test CustomUser model."""

    def test_create_user(self):
        """Test creating a custom user."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            dni="12345678",
            role=User.Role.STUDENT,
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.dni == "12345678"
        assert user.role == User.Role.STUDENT
        assert user.check_password("testpass123")

    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username="testuser",
            first_name="John",
            last_name="Doe",
            dni="12345678",
            role=User.Role.STUDENT,
        )
        assert str(user) == "John Doe"

    def test_dni_unique(self):
        """Test that DNI must be unique."""
        User.objects.create_user(
            username="user1", dni="12345678", role=User.Role.STUDENT
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                username="user2", dni="12345678", role=User.Role.STUDENT
            )


class TestStudentModel:
    """Test Student model."""

    def test_create_student(self, career):
        """Test creating a student."""
        user = User.objects.create_user(
            username="student", dni="11111111", role=User.Role.STUDENT
        )
        student = Student.objects.create(
            student_id="STU00001",
            user=user,
            career=career,
            enrollment_date=date.today(),
        )
        assert student.student_id == "STU00001"
        assert student.user == user
        assert student.career == career

    def test_student_str(self, student_user):
        """Test student string representation."""
        student = student_user.student
        assert "Student ID" in str(student)
        assert student.student_id in str(student)


class TestProfessorModel:
    """Test Professor model."""

    def test_create_professor(self):
        """Test creating a professor."""
        user = User.objects.create_user(
            username="prof", dni="22222222", role=User.Role.PROFESSOR
        )
        professor = Professor.objects.create(
            professor_id="PROF00001",
            user=user,
            degree="PhD",
            category=Professor.Category.TITULAR,
            hire_date=date.today(),
        )
        assert professor.professor_id == "PROF00001"
        assert professor.user == user
        assert professor.degree == "PhD"
        assert professor.category == Professor.Category.TITULAR

    def test_professor_str(self, professor_user):
        """Test professor string representation."""
        professor = professor_user.professor
        assert str(professor) == professor_user.get_full_name()


class TestAdministratorModel:
    """Test Administrator model."""

    def test_create_administrator(self):
        """Test creating an administrator."""
        user = User.objects.create_user(
            username="admin", dni="33333333", role=User.Role.ADMIN
        )
        admin = Administrator.objects.create(
            administrator_id="ADM00001",
            user=user,
            position="Director",
            hire_date=date.today(),
        )
        assert admin.administrator_id == "ADM00001"
        assert admin.user == user
        assert admin.position == "Director"


class TestUserService:
    """Test UserService."""

    def test_create_student_minimal(self):
        """Test creating a student with minimal data."""
        user_data = {
            "username": "newstudent",
            "password": "testpass123",
            "dni": "99999999",
            "first_name": "New",
            "last_name": "Student",
        }
        user = UserService.create_student(user_data)

        assert user.role == User.Role.STUDENT
        assert user.check_password("testpass123")
        assert hasattr(user, "student")
        assert user.student.student_id.startswith("STU")
        assert user.student.enrollment_date == date.today()

    def test_create_student_with_profile_data(self, career):
        """Test creating a student with profile data."""
        user_data = {
            "username": "newstudent",
            "password": "testpass123",
            "dni": "99999999",
        }
        student_data = {
            "career": career,
            "enrollment_date": date(2023, 1, 1),
        }
        user = UserService.create_student(user_data, student_data)

        assert user.student.career == career
        assert user.student.enrollment_date == date(2023, 1, 1)

    def test_create_professor_minimal(self):
        """Test creating a professor with minimal data."""
        user_data = {
            "username": "newprof",
            "password": "testpass123",
            "dni": "88888888",
        }
        user = UserService.create_professor(user_data)

        assert user.role == User.Role.PROFESSOR
        assert hasattr(user, "professor")
        assert user.professor.professor_id.startswith("PROF")
        assert user.professor.degree == "Sin especificar"
        assert user.professor.category == Professor.Category.AUXILIAR

    def test_create_professor_with_profile_data(self):
        """Test creating a professor with profile data."""
        user_data = {
            "username": "newprof",
            "password": "testpass123",
            "dni": "88888888",
        }
        professor_data = {
            "degree": "PhD",
            "category": Professor.Category.TITULAR,
        }
        user = UserService.create_professor(user_data, professor_data)

        assert user.professor.degree == "PhD"
        assert user.professor.category == Professor.Category.TITULAR

    def test_create_administrator_minimal(self):
        """Test creating an administrator with minimal data."""
        user_data = {
            "username": "newadmin",
            "password": "testpass123",
            "dni": "77777777",
        }
        user = UserService.create_administrator(user_data)

        assert user.role == User.Role.ADMIN
        assert hasattr(user, "administrator")
        assert user.administrator.administrator_id.startswith("ADM")
        assert user.administrator.position == "Administrador"

    def test_create_user_profile_for_student(self):
        """Test creating profile for existing student user."""
        user = User.objects.create_user(
            username="student", dni="66666666", role=User.Role.STUDENT
        )
        profile = UserService.create_user_profile(user)

        assert isinstance(profile, Student)
        assert profile.student_id == f"STU{user.id:05d}"
        assert profile.enrollment_date == date.today()

    def test_create_user_profile_for_professor(self):
        """Test creating profile for existing professor user."""
        user = User.objects.create_user(
            username="prof", dni="55555555", role=User.Role.PROFESSOR
        )
        profile = UserService.create_user_profile(user)

        assert isinstance(profile, Professor)
        assert profile.professor_id == f"PROF{user.id:05d}"

    def test_create_user_profile_for_admin(self):
        """Test creating profile for existing admin user."""
        user = User.objects.create_user(
            username="admin", dni="44444444", role=User.Role.ADMIN
        )
        profile = UserService.create_user_profile(user)

        assert isinstance(profile, Administrator)
        assert profile.administrator_id == f"ADM{user.id:05d}"

    def test_update_user_with_profile(self, student_user, career):
        """Test updating user and profile atomically."""
        user_data = {"first_name": "Updated", "email": "updated@test.com"}
        profile_data = {"career": career}

        updated_user = UserService.update_user_with_profile(
            student_user, user_data, profile_data
        )

        assert updated_user.first_name == "Updated"
        assert updated_user.email == "updated@test.com"
        assert updated_user.student.career == career

    def test_update_user_password(self, student_user):
        """Test updating user password."""
        user_data = {"password": "newpassword123"}

        updated_user = UserService.update_user_with_profile(student_user, user_data)

        assert updated_user.check_password("newpassword123")

    def test_update_user_empty_password_ignored(self, student_user):
        """Test that empty password is ignored."""
        old_password = student_user.password
        user_data = {"password": ""}

        updated_user = UserService.update_user_with_profile(student_user, user_data)

        assert updated_user.password == old_password


class TestAssignmentService:
    """Test AssignmentService."""

    def test_update_subject_professor_assignments_add(self, subject, professor):
        """Test adding professor to subject."""
        result = AssignmentService.update_subject_professor_assignments(
            subject, [professor.professor_id]
        )

        assert result["success"] is True
        assert result["changes_made"] is True
        assert professor in subject.professors.all()

    def test_update_subject_professor_assignments_remove(self, subject, professor):
        """Test removing professor from subject."""
        subject.professors.add(professor)
        result = AssignmentService.update_subject_professor_assignments(subject, [])

        assert result["success"] is True
        assert result["changes_made"] is True
        assert professor not in subject.professors.all()

    def test_update_subject_professor_assignments_no_change(self, subject, professor):
        """Test no change when assignments are same."""
        subject.professors.add(professor)
        result = AssignmentService.update_subject_professor_assignments(
            subject, [professor.professor_id]
        )

        assert result["success"] is True
        assert result["changes_made"] is False

    def test_update_final_professor_assignments(self, final_exam, professor):
        """Test updating final exam professor assignments."""
        result = AssignmentService.update_final_professor_assignments(
            final_exam, [professor.professor_id]
        )

        assert result["success"] is True
        assert result["changes_made"] is True
        assert professor in final_exam.professors.all()


class TestUserViews:
    """Test user views."""

    def test_login_view_get(self, client):
        """Test login view GET request."""
        response = client.get(reverse("users:login"))
        assert response.status_code == 200

    def test_login_view_post_success(self, client, student_user):
        """Test successful login."""
        response = client.post(
            reverse("users:login"),
            {"username": "student_test", "password": "testpass123"},
        )
        assert response.status_code == 302  # Redirect after login

    def test_login_view_post_failure(self, client):
        """Test failed login."""
        response = client.post(
            reverse("users:login"),
            {"username": "invalid", "password": "wrong"},
        )
        assert response.status_code == 200  # Stay on page
        assert "form" in response.context

    def test_admin_dashboard_requires_login(self, client):
        """Test admin dashboard requires authentication."""
        response = client.get(reverse("users:admin-dashboard"))
        assert response.status_code == 302  # Redirect to login

    def test_admin_dashboard_requires_admin_role(self, client, student_user):
        """Test admin dashboard requires admin role."""
        client.force_login(student_user)
        response = client.get(reverse("users:admin-dashboard"))
        assert response.status_code == 403  # Permission denied

    def test_user_list_requires_admin(self, client, student_user):
        """Test user list requires admin."""
        client.force_login(student_user)
        response = client.get(reverse("users:user-list"))
        assert response.status_code == 403  # Permission denied

    def test_user_list_success(self, client, admin_user):
        """Test user list for admin."""
        client.force_login(admin_user)
        response = client.get(reverse("users:user-list"))
        assert response.status_code == 200
        assert "users" in response.context

    def test_logout(self, client, student_user):
        """Test logout."""
        client.force_login(student_user)
        response = client.get(reverse("users:logout"))
        assert response.status_code == 302
