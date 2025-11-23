"""Django admin registrations for the app.

Consolidates all admin configurations from the old apps:
- CustomUser, Student, Professor, Administrator (from users)
- Faculty, Career, Subject, FinalExam, Grade (from academics)
- SubjectInscription, FinalExamInscription (from inscriptions)
"""

from django.contrib import admin
from app.models import (
    CustomUser, Student, Professor, Administrator,
    Faculty, Career, Subject, FinalExam, Grade,
    SubjectInscription, FinalExamInscription
)


# User models
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin for CustomUser: username, role, DNI, and email."""
    list_display = ("username", "role", "dni", "email")
    search_fields = ("username", "dni", "email")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student: identity, career, and enrollment date."""
    list_display = ("student_id", "user", "career", "enrollment_date")
    search_fields = ("student_id", "user__username", "career__name")


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    """Admin for Professor: identity, degree, category, and hire date."""
    list_display = ("professor_id", "user", "degree", "category", "hire_date")
    search_fields = ("professor_id", "user__username", "degree")


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    """Admin for Administrator: identity, position, and hire date."""
    list_display = ("administrator_id", "user", "position", "hire_date")
    search_fields = ("administrator_id", "user__username", "position")


# Academic models
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """Admin for Faculty: list key identity fields and enable basic search."""
    list_display = ("code", "name", "dean", "established_date", "website")
    search_fields = ("code", "name", "dean", "email")


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    """Admin for Career: show program metadata with faculty relation."""
    list_display = ("code", "name", "faculty", "director", "duration_years")
    search_fields = ("code", "name", "director", "faculty__name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin for Subject: curriculum fields and quick search."""
    list_display = ("code", "name", "career", "year", "period", "category", "semanal_hours")
    search_fields = ("code", "name", "career__name")


@admin.register(FinalExam)
class FinalExamAdmin(admin.ModelAdmin):
    """Admin for FinalExam: scheduling fields and subject lookup."""
    list_display = ("subject", "date", "call_number", "location", "duration")
    search_fields = ("subject__name", "subject__code", "location")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin for Grade: student, subject, status and grades overview."""
    list_display = ("student", "subject", "status", "promotion_grade", "final_grade")
    search_fields = ("student__user__username", "subject__name", "subject__code")


# Inscription models
@admin.register(SubjectInscription)
class SubjectInscriptionAdmin(admin.ModelAdmin):
    """Admin for SubjectInscription: student, subject and inscription date."""
    list_display = ("student", "subject", "inscription_date")
    search_fields = ("student__user__username", "subject__name", "subject__code")


@admin.register(FinalExamInscription)
class FinalExamInscriptionAdmin(admin.ModelAdmin):
    """Admin for FinalExamInscription: student, final exam and inscription date."""
    list_display = ("student", "final_exam", "inscription_date")
    search_fields = ("student__user__username", "final_exam__subject__name", "final_exam__subject__code")