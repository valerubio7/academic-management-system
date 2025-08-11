from django.contrib import admin
from .models import SubjectInscription, FinalExamInscription


@admin.register(SubjectInscription)
class SubjectInscriptionAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "inscription_date")
    search_fields = ("student__user__username", "subject__name", "subject__code")


@admin.register(FinalExamInscription)
class FinalExamInscriptionAdmin(admin.ModelAdmin):
    list_display = ("student", "final_exam", "inscription_date")
    search_fields = ("student__user__username", "final_exam__subject__name", "final_exam__subject__code")
