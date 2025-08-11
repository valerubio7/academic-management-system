
from django.contrib import admin
from .models import Faculty, Career, Subject, FinalExam, Grade


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "dean", "established_date", "website")
    search_fields = ("code", "name", "dean", "email")


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "faculty", "director", "duration_years")
    search_fields = ("code", "name", "director", "faculty__name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "career", "year", "period", "category", "semanal_hours")
    search_fields = ("code", "name", "career__name")


@admin.register(FinalExam)
class FinalExamAdmin(admin.ModelAdmin):
    list_display = ("subject", "date", "call_number", "location", "duration")
    search_fields = ("subject__name", "subject__code", "location")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "status", "promotion_grade", "final_grade")
    search_fields = ("student__user__username", "subject__name", "subject__code")
