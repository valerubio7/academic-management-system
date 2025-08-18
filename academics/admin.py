"""Django admin registrations for the Academics app.

Registers Faculty, Career, Subject, FinalExam, and Grade with basic list and search configuration.
"""

from django.contrib import admin
from .models import Faculty, Career, Subject, FinalExam, Grade


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
