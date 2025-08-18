"""Core user and profile models.

Defines:
- CustomUser: extends Django's AbstractUser with role and identity fields.
- Student: one-to-one profile linked to a Career.
- Professor: one-to-one profile with teaching assignments and category.
- Administrator: one-to-one profile for administrative staff.

Notes:
    - db_table is set for each model to keep stable table names.
    - One-to-one relations ensure a single profile per CustomUser.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user extending AbstractUser with roles and identity fields.

    Attributes:
        role (str): One of Role choices: {'administrator', 'professor', 'student'}.
        dni (str): National ID; unique.
        phone (str | None): Optional phone number.
        birth_date (date | None): Optional birth date.
        address (str | None): Optional address.
    """

    class Role(models.TextChoices):
        """User roles in the system."""
        ADMIN = 'administrator', 'Administrator'
        PROFESSOR = 'professor', 'Professor'
        STUDENT = 'student', 'Student'

    role = models.CharField(max_length=20, choices=Role.choices, blank=False, null=False)
    dni = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        """Meta options for CustomUser."""
        db_table = 'users'

    def __str__(self):
        """Return full name for admin readability."""
        return f"{self.get_full_name()}"


class Student(models.Model):
    """
    Student profile linked one-to-one with a CustomUser.

    Attributes:
        student_id (str): Unique student identifier (primary key).
        user (CustomUser): Related user account.
        career (academics.Career | None): Degree program; nullable if unset.
        enrollment_date (date): Enrollment date.
    """
    student_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student')
    career = models.ForeignKey('academics.Career', on_delete=models.SET_NULL, null=True, related_name='students')
    enrollment_date = models.DateField()

    class Meta:
        """Meta options for Student."""
        db_table = 'students'

    def __str__(self):
        """Readable identifier combining student_id and full name."""
        return f"Student ID {self.student_id} - {self.user.get_full_name()}"


class Professor(models.Model):
    """
    Professor profile with subjects/final exams assignments.

    Attributes:
        professor_id (str): Unique professor identifier (primary key).
        user (CustomUser): Related user account.
        subjects (QuerySet[academics.Subject]): Taught subjects (M2M).
        final_exams (QuerySet[academics.FinalExam]): Assigned final exams (M2M).
        degree (str): Academic degree.
        hire_date (date): Hiring date.
        category (str): One of Category choices.
    """

    class Category(models.TextChoices):
        """Category choices for professors."""
        TITULAR = 'titular', 'Titular'
        ADJUNCT = 'adjunct', 'Adjunct'
        AUXILIAR = 'auxiliar', 'Auxiliar'

    professor_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='professor')
    subjects = models.ManyToManyField('academics.Subject', related_name='professors', blank=True)
    final_exams = models.ManyToManyField('academics.FinalExam', related_name='professors', blank=True)
    degree = models.CharField(max_length=100)
    hire_date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)

    class Meta:
        """Meta options for Professor."""
        db_table = 'professors'

    def __str__(self):
        """Return full name for admin readability."""
        return f"{self.user.get_full_name()}"


class Administrator(models.Model):
    """
    Administrator profile for non-teaching staff.

    Attributes:
        administrator_id (str): Unique identifier (primary key).
        user (CustomUser): Related user account.
        position (str): Job position/title.
        hire_date (date): Hiring date.
    """
    administrator_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='administrator')
    position = models.CharField(max_length=100)
    hire_date = models.DateField()

    class Meta:
        """Meta options for Administrator."""
        db_table = 'administrators'

    def __str__(self):
        """Return full name for admin readability."""
        return f"{self.user.get_full_name()}"
