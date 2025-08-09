from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom User model that extends Django's AbstractUser."""
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
        """"Meta options for CustomUser."""
        db_table = 'users'

    def __str__(self):
        return f"{self.get_full_name()}"

    @property
    def profile(self):
        """Get the specific profile based on role."""
        if self.role == self.Role.STUDENT:
            return getattr(self, 'student', None)
        elif self.role == self.Role.PROFESSOR:
            return getattr(self, 'professor', None)
        elif self.role == self.Role.ADMIN:
            return getattr(self, 'administrator', None)
        return None


class Student(models.Model):
    """Specific profile for students"""
    student_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student')
    career = models.ForeignKey('academics.Career', on_delete=models.SET_NULL, null=True, related_name='students')
    enrollment_date = models.DateField()

    class Meta:
        """Meta options for Student."""
        db_table = 'students'

    def __str__(self):
        return f"Student ID {self.student_id} - {self.user.get_full_name()}"


class Professor(models.Model):
    """Specific profile for professors"""
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
        return f"{self.user.get_full_name()}"


class Administrator(models.Model):
    """Specific profile for administrators"""
    administrator_id = models.CharField(max_length=20, unique=True, primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='administrator')
    position = models.CharField(max_length=100)
    hire_date = models.DateField()

    class Meta:
        """Meta options for Admin."""
        db_table = 'administrators'

    def __str__(self):
        return f"{self.user.get_full_name()}"
