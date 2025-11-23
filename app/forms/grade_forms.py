"""
Grade forms for the app.

Provides forms for grade management by professors.
"""

from django import forms
from app.models import Grade


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