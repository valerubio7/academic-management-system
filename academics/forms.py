from django import forms
from .models import Faculty, Career, Subject, FinalExam, Grade


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'code', 'address', 'phone', 'email', 'website', 'dean', 'established_date', 'description']


class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = ['name', 'code', 'faculty', 'director', 'duration_years', 'description']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'career', 'year', 'category', 'period', 'semanal_hours', 'description']


class FinalExamForm(forms.ModelForm):
    class Meta:
        model = FinalExam
        fields = ['subject', 'date', 'location', 'duration', 'call_number', 'notes']


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['promotion_grade', 'status', 'final_grade', 'notes']
