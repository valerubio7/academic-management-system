from django import forms
from users.models import CustomUser, Student, Professor, Administrator
from academics.models import Career


class UserBaseForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'dni',
            'phone', 'birth_date', 'address', 'role', 'is_active'
        ]


class StudentProfileForm(forms.ModelForm):
    career = forms.ModelChoiceField(queryset=Career.objects.all(), label="Carrera")

    class Meta:
        model = Student
        fields = ['student_id', 'career', 'enrollment_date']
        labels = {
            'student_id': 'Legajo Estudiante',
            'enrollment_date': 'Fecha de Ingreso',
        }


class ProfessorProfileForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['professor_id', 'degree', 'category', 'hire_date']
        labels = {
            'professor_id': 'Legajo Profesor',
            'degree': 'Título',
            'category': 'Categoría',
            'hire_date': 'Fecha de Alta',
        }


class AdministratorProfileForm(forms.ModelForm):
    class Meta:
        model = Administrator
        fields = ['administrator_id', 'position', 'hire_date']
        labels = {
            'administrator_id': 'Legajo Administrador',
            'position': 'Cargo',
            'hire_date': 'Fecha de Alta',
        }
