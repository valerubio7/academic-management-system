"""Student views for the app.

Includes:
- Dashboard
- Subject inscriptions
- Final exam inscriptions  
- Certificate downloads
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.models import CustomUser, Subject, FinalExam
from app.services import StudentService, InscriptionService, CertificateService


def is_student(user):
    """Return True if the user is authenticated and has student role."""
    return user.is_authenticated and user.role == CustomUser.Role.STUDENT


def is_student_with_profile(user):
    """Return True if the user is authenticated, has student role and student profile."""
    return (user.is_authenticated and
            user.role == CustomUser.Role.STUDENT and
            hasattr(user, 'student'))


@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """
    Render student dashboard.

    Returns:
        HttpResponse: Dashboard page with student data.
    """
    try:
        student_service = StudentService()
        dashboard_data = student_service.get_student_dashboard_data(request.user)
        return render(request, "app/student/dashboard.html", dashboard_data)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("home")


@login_required
@user_passes_test(is_student)
def subject_inscribe(request, subject_code):
    """
    Create subject inscription.

    Args:
        subject_code (str): Subject code (PK).

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    student = request.user.student
    subject = get_object_or_404(Subject, code=subject_code, career=student.career)
    
    if request.method == "POST":
        try:
            inscription_service = InscriptionService()
            result = inscription_service.inscribe_student_to_subject(student, subject)
            
            if result['inscription_created']:
                messages.success(request, "Inscripción a la materia realizada.")
            else:
                messages.info(request, "Ya estabas inscripto en esta materia.")
        except Exception as e:
            messages.error(request, f"Error en la inscripción: {str(e)}")
        
        return redirect("app:student-dashboard")
    
    return render(request, "app/student/inscribe_confirm.html", {"subject": subject})


@login_required
@user_passes_test(is_student)
def final_exam_inscribe(request, final_exam_id):
    """
    Create final exam inscription.

    Args:
        final_exam_id (int): FinalExam primary key.

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    student = request.user.student
    final_exam = get_object_or_404(FinalExam, pk=final_exam_id, subject__career=student.career)
    
    # Check if student can inscribe (has REGULAR status)
    inscription_service = InscriptionService()
    try:
        inscription_service._validate_final_exam_inscription_requirements(student, final_exam)
    except Exception:
        # Redirect if cannot inscribe
        return redirect("app:student-dashboard")
    
    if request.method == "POST":
        try:
            inscription_service.inscribe_student_to_final_exam(student, final_exam)
            messages.success(request, "Inscripción al final realizada.")
        except Exception as e:
            messages.error(request, str(e))
        
        return redirect("app:student-dashboard")
    
    return render(request, "app/student/inscribe_confirm.html", {"final_exam": final_exam})


@login_required
def download_regular_certificate(request):
    """
    Generate and download a 'regular student' certificate as DOCX.
    """
    # Check if user has student profile
    if not is_student_with_profile(request.user):
        return redirect("home")
    
    try:
        certificate_service = CertificateService()
        output = certificate_service.generate_regular_certificate(request.user)
        filename = certificate_service.get_regular_certificate_filename(request.user)
        
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response
        
    except Exception as e:
        messages.error(request, str(e))
        return redirect("app:student-dashboard")