"""Professor views for the app.

Includes:
- Dashboard
- Grade management
- Final exam inscriptions management
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from app.forms.grade_forms import GradeForm
from app.models import CustomUser, Subject, Grade
from app.services import ProfessorService, GradeService


def is_professor(user):
    """Return True if the user is authenticated and has professor role."""
    return user.is_authenticated and user.role == CustomUser.Role.PROFESSOR


@login_required
@user_passes_test(is_professor)
def professor_dashboard(request):
    """
    Render professor dashboard.

    Returns:
        HttpResponse: Dashboard page with professor data.
    """
    try:
        professor_service = ProfessorService()
        dashboard_data = professor_service.get_professor_dashboard_data(request.user)
        return render(request, "app/professor/dashboard.html", dashboard_data)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("home")


@login_required
@user_passes_test(is_professor)
def grade_list(request, subject_code):
    """
    List grades for a subject.

    Args:
        subject_code (str): Subject code (PK) assigned to the professor.

    Returns:
        HttpResponse: Page with grades queryset.
    """
    professor = request.user.professor
    subject = get_object_or_404(Subject, code=subject_code, professors=professor)
    
    try:
        grade_service = GradeService()
        grades = grade_service.get_subject_grades_with_backfill(subject, professor)
        return render(request, "app/professor/grade_list.html", {"grades": grades, "subject": subject})
    except Exception as e:
        messages.error(request, f"Error al obtener calificaciones: {str(e)}")
        return redirect("app:professor-dashboard")


@login_required
@user_passes_test(is_professor)
def grade_edit(request, pk):
    """
    Edit a grade record for a student in a professor's subject.

    Args:
        pk (int): Grade primary key.

    Returns:
        HttpResponse: Redirect to grade list on success or form page on error.
    """
    grade = get_object_or_404(Grade, pk=pk)
    grade_service = GradeService()
    
    try:
        # Validate permissions through service
        grade_service.validate_grade_edit_permissions(grade, request.user.professor)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("app:professor-dashboard")

    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            try:
                grade_service.update_grade(grade, form.cleaned_data)
                return redirect("app:grade-list", subject_code=grade.subject.code)
            except Exception as e:
                messages.error(request, f"Error al actualizar calificación: {str(e)}")
    else:
        form = GradeForm(instance=grade)
    
    return render(request, "app/professor/grade_form.html", {"form": form, "grade": grade})


@login_required
@user_passes_test(is_professor)
def professor_final_inscriptions(request, final_exam_id):
    """
    List final exam inscriptions assigned to the professor.

    Args:
        final_exam_id (int): FinalExam primary key.

    Returns:
        HttpResponse: Page with inscriptions queryset.
    """
    try:
        professor_service = ProfessorService()
        inscriptions_data = professor_service.get_final_exam_inscriptions(final_exam_id, request.user.professor)
        return render(request, "app/professor/final_inscriptions.html", inscriptions_data)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("app:professor-dashboard")
