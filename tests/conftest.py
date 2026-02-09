"""Pytest fixtures for tests."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

from academics.models import Career, Faculty, Subject
from enrollments.models import FinalExam, FinalExamInscription, SubjectInscription
from grading.models import Grade
from users.models import Administrator, Professor, Student

User = get_user_model()


@pytest.fixture
def faculty():
    """Create a test faculty."""
    return Faculty.objects.create(
        code="FAC001",
        name="Faculty of Engineering",
        address="123 Main St",
        phone="+1234567890",
        email="faculty@example.com",
        website="https://faculty.example.com",
        dean="Dr. John Doe",
        established_date=date(2000, 1, 1),
        description="Test faculty",
    )


@pytest.fixture
def career(faculty):
    """Create a test career."""
    return Career.objects.create(
        code="CAR001",
        name="Computer Science",
        faculty=faculty,
        director="Dr. Jane Smith",
        duration_years=5,
        description="Test career",
    )


@pytest.fixture
def subject(career):
    """Create a test subject."""
    return Subject.objects.create(
        code="SUB001",
        name="Programming 1",
        career=career,
        year=1,
        category=Subject.Category.OBLIGATORY,
        period=Subject.Period.FIRST,
        semanal_hours=6,
        description="Test subject",
    )


@pytest.fixture
def subject2(career):
    """Create a second test subject."""
    return Subject.objects.create(
        code="SUB002",
        name="Mathematics 1",
        career=career,
        year=1,
        category=Subject.Category.OBLIGATORY,
        period=Subject.Period.FIRST,
        semanal_hours=4,
        description="Test subject 2",
    )


@pytest.fixture
def admin_user():
    """Create a test admin user."""
    user = User.objects.create_user(
        username="admin_test",
        email="admin@test.com",
        password="testpass123",
        first_name="Admin",
        last_name="User",
        dni="12345678",
        role=User.Role.ADMIN,
    )
    Administrator.objects.create(
        administrator_id=f"ADM{user.id:05d}",
        user=user,
        position="Test Admin",
        hire_date=date.today(),
    )
    return user


@pytest.fixture
def professor_user():
    """Create a test professor user."""
    user = User.objects.create_user(
        username="prof_test",
        email="prof@test.com",
        password="testpass123",
        first_name="Professor",
        last_name="User",
        dni="87654321",
        role=User.Role.PROFESSOR,
    )
    Professor.objects.create(
        professor_id=f"PROF{user.id:05d}",
        user=user,
        degree="PhD",
        category=Professor.Category.TITULAR,
        hire_date=date.today(),
    )
    return user


@pytest.fixture
def student_user(career):
    """Create a test student user."""
    user = User.objects.create_user(
        username="student_test",
        email="student@test.com",
        password="testpass123",
        first_name="Student",
        last_name="User",
        dni="11223344",
        role=User.Role.STUDENT,
    )
    Student.objects.create(
        student_id=f"STU{user.id:05d}",
        user=user,
        career=career,
        enrollment_date=date.today(),
    )
    return user


@pytest.fixture
def student_user2(career):
    """Create a second test student user."""
    user = User.objects.create_user(
        username="student_test2",
        email="student2@test.com",
        password="testpass123",
        first_name="Second",
        last_name="Student",
        dni="99887766",
        role=User.Role.STUDENT,
    )
    Student.objects.create(
        student_id=f"STU{user.id:05d}",
        user=user,
        career=career,
        enrollment_date=date.today(),
    )
    return user


@pytest.fixture
def professor(professor_user):
    """Get the professor profile."""
    return professor_user.professor


@pytest.fixture
def student(student_user):
    """Get the student profile."""
    return student_user.student


@pytest.fixture
def student2(student_user2):
    """Get the second student profile."""
    return student_user2.student


@pytest.fixture
def final_exam(subject):
    """Create a test final exam."""
    return FinalExam.objects.create(
        subject=subject,
        date=date.today() + timedelta(days=30),
        location="Room 101",
        duration=timedelta(hours=2),
        call_number=1,
        notes="First call",
    )


@pytest.fixture
def subject_inscription(student, subject):
    """Create a subject inscription."""
    return SubjectInscription.objects.create(student=student, subject=subject)


@pytest.fixture
def grade(student, subject):
    """Create a grade record."""
    return Grade.objects.create(
        student=student, subject=subject, status=Grade.StatusSubject.FREE
    )


@pytest.fixture
def final_exam_inscription(student, final_exam):
    """Create a final exam inscription."""
    return FinalExamInscription.objects.create(student=student, final_exam=final_exam)
