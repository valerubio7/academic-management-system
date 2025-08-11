from django.contrib import admin
from .models import CustomUser, Student, Professor, Administrator


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "role", "dni", "email")
    search_fields = ("username", "dni", "email")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "user", "career", "enrollment_date")
    search_fields = ("student_id", "user__username", "career__name")


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("professor_id", "user", "degree", "category", "hire_date")
    search_fields = ("professor_id", "user__username", "degree")


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("administrator_id", "user", "position", "hire_date")
    search_fields = ("administrator_id", "user__username", "position")
