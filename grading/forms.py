from django import forms
from grading.models import Grade


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["promotion_grade", "final_grade", "notes"]
        labels = {
            "promotion_grade": "Nota de Promoción",
            "final_grade": "Nota Final",
            "notes": "Notas/Observaciones",
        }
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
