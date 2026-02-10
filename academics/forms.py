from django import forms

from academics.models import Career, Faculty, Subject


class FacultyForm(forms.ModelForm):
    website = forms.URLField(required=False, label="Sitio Web", assume_scheme="https")

    class Meta:
        model = Faculty
        fields = [
            "name",
            "code",
            "address",
            "phone",
            "email",
            "website",
            "dean",
            "established_date",
            "description",
        ]
        labels = {
            "name": "Nombre",
            "code": "Código",
            "address": "Dirección",
            "phone": "Teléfono",
            "email": "Email",
            "dean": "Decano",
            "established_date": "Fecha de Fundación",
            "description": "Descripción",
        }


class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = [
            "name",
            "code",
            "faculty",
            "director",
            "duration_years",
            "description",
        ]
        labels = {
            "name": "Nombre",
            "code": "Código",
            "faculty": "Facultad",
            "director": "Director",
            "duration_years": "Duración (años)",
            "description": "Descripción",
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            "name",
            "code",
            "career",
            "year",
            "category",
            "period",
            "semanal_hours",
            "description",
        ]
        labels = {
            "name": "Nombre",
            "code": "Código",
            "career": "Carrera",
            "year": "Año",
            "category": "Categoría",
            "period": "Período",
            "semanal_hours": "Horas Semanales",
            "description": "Descripción",
        }
