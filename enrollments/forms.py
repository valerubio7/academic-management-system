from django import forms

from enrollments.models import FinalExam


class FinalExamForm(forms.ModelForm):
    class Meta:
        model = FinalExam
        fields = ["subject", "date", "location", "duration", "call_number", "notes"]
        labels = {
            "subject": "Materia",
            "date": "Fecha",
            "location": "Ubicación",
            "duration": "Duración (minutos)",
            "call_number": "Número de Llamado",
            "notes": "Notas",
        }
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
