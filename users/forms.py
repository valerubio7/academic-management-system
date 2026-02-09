from django import forms

from academics.models import Career
from users.models import Administrator, CustomUser, Professor, Student


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)


class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput, strip=False, required=False
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
        strip=False,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "dni",
            "phone",
            "birth_date",
            "address",
            "role",
            "is_active",
        ]
        labels = {
            "username": "Usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Email",
            "dni": "DNI",
            "phone": "Teléfono",
            "birth_date": "Fecha de Nacimiento",
            "address": "Dirección",
            "role": "Rol",
            "is_active": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["password1"].required = False
            self.fields["password2"].required = False
            self.fields["role"].disabled = True
            self.fields[
                "role"
            ].help_text = "El rol no puede ser modificado una vez creado el usuario."
        else:
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")

        if self.instance and self.instance.pk:
            if pwd1 or pwd2:
                if not pwd1:
                    self.add_error("password1", "Ingrese una contraseña.")
                if not pwd2:
                    self.add_error("password2", "Confirme la contraseña.")
                if pwd1 and pwd2 and pwd1 != pwd2:
                    self.add_error("password2", "Las contraseñas no coinciden.")
        else:
            if not pwd1 or not pwd2:
                self.add_error("password1", "Ingrese una contraseña.")
            elif pwd1 != pwd2:
                self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get("password1")
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


class StudentProfileForm(forms.ModelForm):
    career = forms.ModelChoiceField(
        queryset=Career.objects.all(),
        label="Carrera",
        required=False,
        empty_label="(Sin carrera asignada)",
    )

    class Meta:
        model = Student
        fields = ["student_id", "career", "enrollment_date"]
        labels = {
            "student_id": "Legajo Estudiante",
            "enrollment_date": "Fecha de Ingreso",
        }


class ProfessorProfileForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ["professor_id", "degree", "category", "hire_date"]
        labels = {
            "professor_id": "Legajo Profesor",
            "degree": "Título",
            "category": "Categoría",
            "hire_date": "Fecha de Alta",
        }
        widgets = {"category": forms.Select(choices=Professor.Category.choices)}


class AdministratorProfileForm(forms.ModelForm):
    class Meta:
        model = Administrator
        fields = ["administrator_id", "position", "hire_date"]
        labels = {
            "administrator_id": "Legajo Administrador",
            "position": "Cargo",
            "hire_date": "Fecha de Alta",
        }
