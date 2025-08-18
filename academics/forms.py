"""
ModelForm definitions for the Academics app.

Provides forms to create and edit:
- Faculty: institution information.
- Career: academic programs within a faculty.
- Subject: courses belonging to a career.
- FinalExam: final exam sessions for a subject.
- Grade: student grades and academic status.

Example:
    Typical usage in a view:

    >>> def create_subject(request):
    ...     form = SubjectForm(request.POST or None)
    ...     if form.is_valid():
    ...         form.save()
    ...         return redirect("subject_list")
    ...     return render(request, "subjects/subject_form.html", {"form": form})
"""

from django import forms
from .models import Faculty, Career, Subject, FinalExam, Grade


class FacultyForm(forms.ModelForm):
    """
    ModelForm to create or update a Faculty instance.

    Purpose:
    - Exposes core institutional fields for admin/CRUD screens.
    - Applies model-level validation through Django's ModelForm.

    Fields:
    - name, code, address, phone, email, website, dean, established_date, description
    """

    class Meta:
        model = Faculty
        fields = ['name', 'code', 'address', 'phone', 'email', 'website', 'dean', 'established_date', 'description']


class CareerForm(forms.ModelForm):
    """
    ModelForm to create or update a Career (degree program).

    Notes:
    - Related selections (e.g., faculty) can be restricted in the view if needed.
    - Business rules should live in the model clean() methods.

    Fields:
    - name, code, faculty, director, duration_years, description
    """

    class Meta:
        model = Career
        fields = ['name', 'code', 'faculty', 'director', 'duration_years', 'description']


class SubjectForm(forms.ModelForm):
    """
    ModelForm to create or update a Subject (course).

    Typical usage:
    - Manage curriculum (course catalog) in staff dashboards.
    - Leverages model validators for year/category/period fields.

    Fields:
    - name, code, career, year, category, period, semanal_hours, description
    """

    class Meta:
        model = Subject
        fields = ['name', 'code', 'career', 'year', 'category', 'period', 'semanal_hours', 'description']


class FinalExamForm(forms.ModelForm):
    """
    ModelForm to create or update a FinalExam session.

    Typical usage:
    - Schedule exam calls for a subject with date/time/location metadata.

    Fields:
    - subject, date, location, duration, call_number, notes
    """

    class Meta:
        model = FinalExam
        fields = ['subject', 'date', 'location', 'duration', 'call_number', 'notes']


class GradeForm(forms.ModelForm):
    """
    ModelForm to create or update a Grade.

    Notes:
    - Captures promotion/regular status and final grade values.
    - Status transition rules should be enforced in the model.

    Fields:
    - promotion_grade, status, final_grade, notes
    """

    class Meta:
        model = Grade
        fields = ['promotion_grade', 'status', 'final_grade', 'notes']
