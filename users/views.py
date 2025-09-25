"""Views for Users app: admin, student, and professor workflows.

Includes:
- Admin: CRUD for users, faculties, careers, subjects, finals, and assignments.
- Student: dashboard, subject/final inscriptions, regular certificate.
- Professor: dashboard, grade management, final inscriptions.

Notes:
    - Access control via role-based predicates (is_admin/is_student/is_professor).
    - Uses messages framework for user feedback.
    - Keeps business rules minimal in views; core rules live in models/services.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from academics.forms import CareerForm, FacultyForm, FinalExamForm, GradeForm, SubjectForm
from app.models import (
    Career, Faculty, FinalExam, Grade, Subject, CustomUser
)
from app.repositories import (
    FacultyRepository, CareerRepository,
    SubjectRepository, FinalExamRepository
)
from app.services import UserManagementService
from users.forms import AdministratorProfileForm, ProfessorProfileForm, StudentProfileForm, UserForm


# --------- Admin Views -------
def is_admin(user):
    """Return True if the user is authenticated and has administrator role."""
    return user.is_authenticated and user.role == CustomUser.Role.ADMIN


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Render the admin dashboard.

    Returns:
        HttpResponse: Admin dashboard page.
    """
    return render(request, "users/admin_dashboard.html")


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """
    List all users.

    Returns:
        HttpResponse: Page with user queryset.
    """
    user_service = UserManagementService()
    users = user_service.list_all_users_with_profiles()
    return render(request, "users/user_list.html", {"users": users})


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """
    Create a new user with mandatory role-specific profile.

    Returns:
        HttpResponse: Redirect to list on success or form page on error.
    """
    user_service = UserManagementService()
    selected_role = None
    
    if request.method == "POST":
        user_form = UserForm(request.POST)
        selected_role = request.POST.get("role")
        student_profile_form = StudentProfileForm(request.POST)
        professor_profile_form = ProfessorProfileForm(request.POST)
        administrator_profile_form = AdministratorProfileForm(request.POST)

        if selected_role == CustomUser.Role.STUDENT:
            profile_form = student_profile_form
        elif selected_role == CustomUser.Role.PROFESSOR:
            profile_form = professor_profile_form
        elif selected_role == CustomUser.Role.ADMIN:
            profile_form = administrator_profile_form
        else:
            profile_form = None

        # Validate that both user form and profile form are valid
        # Profile form is now mandatory when a role is selected
        forms_valid = user_form.is_valid()
        if profile_form is not None:
            forms_valid = forms_valid and profile_form.is_valid()
        elif selected_role:  # Role selected but no matching profile form
            messages.error(request, "Debe seleccionar un rol válido y completar los datos del perfil.")
            forms_valid = False

        if forms_valid:
            try:
                # Use form's save method to handle password hashing
                user = user_form.save()
                profile_data = profile_form.cleaned_data if profile_form else {}
                
                # Create profile for the user
                user_service._create_profile_for_user(user, profile_data)
                messages.success(request, "Usuario creado correctamente.")
                return redirect("users:user-list")
            except Exception as e:
                messages.error(request, f"Error al crear usuario: {str(e)}")
    else:
        user_form = UserForm()
        student_profile_form = StudentProfileForm()
        professor_profile_form = ProfessorProfileForm()
        administrator_profile_form = AdministratorProfileForm()
        
    return render(request, "users/user_form.html", {
        "user_form": user_form,
        "student_profile_form": student_profile_form,
        "professor_profile_form": professor_profile_form,
        "administrator_profile_form": administrator_profile_form,
        "selected_role": selected_role
    })


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    """
    Update a user and its role-specific profile. Role cannot be changed.

    Args:
        pk (int): User primary key.

    Returns:
        HttpResponse: Redirect to list on success or form page on error.
    """
    user = get_object_or_404(CustomUser, pk=pk)
    user_service = UserManagementService()
    
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            role = user_form.cleaned_data["role"]
            student_instance = (getattr(user, "student", None) if role == CustomUser.Role.STUDENT else None)
            professor_instance = (getattr(user, "professor", None) if role == CustomUser.Role.PROFESSOR else None)
            administrator_instance = (getattr(user, "administrator", None) if role == CustomUser.Role.ADMIN else None)

            student_profile_form = StudentProfileForm(request.POST, instance=student_instance)
            professor_profile_form = ProfessorProfileForm(request.POST, instance=professor_instance)
            administrator_profile_form = AdministratorProfileForm(request.POST, instance=administrator_instance)

            if role == CustomUser.Role.STUDENT:
                profile_form = student_profile_form
            elif role == CustomUser.Role.PROFESSOR:
                profile_form = professor_profile_form
            elif role == CustomUser.Role.ADMIN:
                profile_form = administrator_profile_form
            else:
                profile_form = None

            if profile_form is None or profile_form.is_valid():
                try:
                    user_data = user_form.cleaned_data
                    profile_data = profile_form.cleaned_data if profile_form else None
                    
                    user_service.update_user_profile(user, user_data, profile_data)
                    messages.success(request, "Usuario actualizado correctamente.")
                    return redirect("users:user-list")
                except Exception as e:
                    messages.error(request, f"Error al actualizar usuario: {str(e)}")

        posted_role = request.POST.get("role")
        student_profile_form = StudentProfileForm(request.POST)
        professor_profile_form = ProfessorProfileForm(request.POST)
        administrator_profile_form = AdministratorProfileForm(request.POST)
        return render(request, "users/user_form.html", {
            "user_form": user_form,
            "student_profile_form": student_profile_form,
            "professor_profile_form": professor_profile_form,
            "administrator_profile_form": administrator_profile_form,
            "selected_role": posted_role
        })
    else:
        user_form = UserForm(instance=user)
        student_profile_form = StudentProfileForm(instance=getattr(user, "student", None))
        professor_profile_form = ProfessorProfileForm(instance=getattr(user, "professor", None))
        administrator_profile_form = AdministratorProfileForm(instance=getattr(user, "administrator", None))
        return render(request, "users/user_form.html", {
            "user_form": user_form,
            "student_profile_form": student_profile_form,
            "professor_profile_form": professor_profile_form,
            "administrator_profile_form": administrator_profile_form,
            "selected_role": user.role
        })


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    """
    Delete a user after confirmation.

    Args:
        pk (int): User primary key.

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    user = get_object_or_404(CustomUser, pk=pk)
    user_service = UserManagementService()
    
    if request.method == "POST":
        try:
            user_service.delete_user(user)
            messages.success(request, "Usuario eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar usuario: {str(e)}")
        return redirect("users:user-list")
    return render(request, "users/confirm_delete.html", {"user": user})


@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    """
    List faculties.

    Returns:
        HttpResponse: Page with faculties queryset.
    """
    faculties = FacultyRepository().list_all()
    return render(request, "users/faculty_list.html", {"faculties": faculties})


@login_required
@user_passes_test(is_admin)
def faculty_create(request):
    """
    Create a faculty.

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import FacultyService
    
    if request.method == "POST":
        form = FacultyForm(request.POST)
        if form.is_valid():
            try:
                faculty_service = FacultyService()
                faculty_service.create_faculty(form.cleaned_data)
                messages.success(request, "Facultad creada correctamente.")
                return redirect("users:faculty-list")
            except Exception as e:
                messages.error(request, f"Error al crear facultad: {str(e)}")
    else:
        form = FacultyForm()
    return render(request, "users/faculty_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def faculty_edit(request, code):
    """
    Edit a faculty.

    Args:
        code (str): Faculty code (PK).

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import FacultyService
    
    faculty = get_object_or_404(Faculty, code=code)
    if request.method == "POST":
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            try:
                faculty_service = FacultyService()
                faculty_service.update_faculty(faculty, form.cleaned_data)
                messages.success(request, "Facultad actualizada correctamente.")
                return redirect("users:faculty-list")
            except Exception as e:
                messages.error(request, f"Error al actualizar facultad: {str(e)}")
    else:
        form = FacultyForm(instance=faculty)
    return render(request, "users/faculty_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def faculty_delete(request, code):
    """
    Delete a faculty after confirmation.

    Args:
        code (str): Faculty code (PK).

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    from app.services import FacultyService
    
    faculty = get_object_or_404(Faculty, code=code)
    if request.method == "POST":
        try:
            faculty_service = FacultyService()
            faculty_service.delete_faculty(faculty)
            messages.success(request, "Facultad eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar facultad: {str(e)}")
        return redirect("users:faculty-list")
    return render(request, "users/confirm_delete.html", {"object": faculty, "back": "users:faculty-list"})


@login_required
@user_passes_test(is_admin)
def career_list(request):
    """
    List careers.

    Returns:
        HttpResponse: Page with careers queryset.
    """
    careers = CareerRepository().list_all()
    return render(request, "users/career_list.html", {"careers": careers})


@login_required
@user_passes_test(is_admin)
def career_create(request):
    """
    Create a career.

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import CareerService
    
    if request.method == "POST":
        form = CareerForm(request.POST)
        if form.is_valid():
            try:
                career_service = CareerService()
                career_service.create_career(form.cleaned_data)
                messages.success(request, "Carrera creada correctamente.")
                return redirect("users:career-list")
            except Exception as e:
                messages.error(request, f"Error al crear carrera: {str(e)}")
    else:
        form = CareerForm()
    return render(request, "users/career_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def career_edit(request, code):
    """
    Edit a career.

    Args:
        code (str): Career code (PK).

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import CareerService
    
    career = get_object_or_404(Career, code=code)
    if request.method == "POST":
        form = CareerForm(request.POST, instance=career)
        if form.is_valid():
            try:
                career_service = CareerService()
                career_service.update_career(career, form.cleaned_data)
                messages.success(request, "Carrera actualizada correctamente.")
                return redirect("users:career-list")
            except Exception as e:
                messages.error(request, f"Error al actualizar carrera: {str(e)}")
    else:
        form = CareerForm(instance=career)
    return render(request, "users/career_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def career_delete(request, code):
    """
    Delete a career after confirmation.

    Args:
        code (str): Career code (PK).

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    from app.services import CareerService
    
    career = get_object_or_404(Career, code=code)
    if request.method == "POST":
        try:
            career_service = CareerService()
            career_service.delete_career(career)
            messages.success(request, "Carrera eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar carrera: {str(e)}")
        return redirect("users:career-list")
    return render(request, "users/confirm_delete.html", {"object": career, "back": "users:career-list"})


@login_required
@user_passes_test(is_admin)
def subject_list(request):
    """
    List subjects.

    Returns:
        HttpResponse: Page with subjects queryset.
    """
    subjects = SubjectRepository().list_all_with_career()
    return render(request, "users/subject_list.html", {"subjects": subjects})


@login_required
@user_passes_test(is_admin)
def subject_create(request):
    """
    Create a subject.

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import SubjectService
    
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            try:
                subject_service = SubjectService()
                subject_service.create_subject(form.cleaned_data)
                messages.success(request, "Materia creada correctamente.")
                return redirect("users:subject-list")
            except Exception as e:
                messages.error(request, f"Error al crear materia: {str(e)}")
    else:
        form = SubjectForm()
    return render(request, "users/subject_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def subject_edit(request, code):
    """
    Edit a subject.

    Args:
        code (str): Subject code (PK).

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import SubjectService
    
    subject = get_object_or_404(Subject, code=code)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            try:
                subject_service = SubjectService()
                subject_service.update_subject(subject, form.cleaned_data)
                messages.success(request, "Materia actualizada correctamente.")
                return redirect("users:subject-list")
            except Exception as e:
                messages.error(request, f"Error al actualizar materia: {str(e)}")
    else:
        form = SubjectForm(instance=subject)
    return render(request, "users/subject_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def subject_delete(request, code):
    """
    Delete a subject after confirmation.

    Args:
        code (str): Subject code (PK).

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    from app.services import SubjectService
    
    subject = get_object_or_404(Subject, code=code)
    if request.method == "POST":
        try:
            subject_service = SubjectService()
            subject_service.delete_subject(subject)
            messages.success(request, "Materia eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar materia: {str(e)}")
        return redirect("users:subject-list")
    return render(request, "users/confirm_delete.html", {"object": subject, "back": "users:subject-list"})


@login_required
@user_passes_test(is_admin)
def assign_subject_professors(request, code):
    """
    Assign/remove professors for a subject.

    Args:
        code (str): Subject code (PK).

    Returns:
        HttpResponse: Redirect to list after processing or form page (GET).
    """
    from app.services import AssignmentService
    
    subject = get_object_or_404(Subject, code=code)
    
    if request.method == "POST":
        try:
            assignment_service = AssignmentService()
            selected_ids = request.POST.getlist("professors")
            result = assignment_service.update_subject_professor_assignments(code, selected_ids)
            
            if result['changes_made']:
                messages.success(request, result['message'])
            else:
                messages.info(request, result['message'])
        except Exception as e:
            messages.error(request, f"Error en las asignaciones: {str(e)}")
            
        return redirect("users:subject-list")

    assignment_service = AssignmentService()
    professors = assignment_service.get_all_professors()
    return render(request, "users/assign_professors.html", {"subject": subject, "professors": professors})


@login_required
@user_passes_test(is_admin)
def final_list(request):
    """
    List final exams.

    Returns:
        HttpResponse: Page with final exams queryset.
    """
    finals = FinalExamRepository().list_all_with_subject()
    return render(request, "users/final_list.html", {"finals": finals})


@login_required
@user_passes_test(is_admin)
def final_create(request):
    """
    Create a final exam.

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import FinalExamService
    
    if request.method == "POST":
        form = FinalExamForm(request.POST)
        if form.is_valid():
            try:
                final_exam_service = FinalExamService()
                final_exam_service.create_final_exam(form.cleaned_data)
                messages.success(request, "Final creado correctamente.")
                return redirect("users:final-list")
            except Exception as e:
                messages.error(request, f"Error al crear final: {str(e)}")
    else:
        form = FinalExamForm()
    return render(request, "users/final_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def final_edit(request, pk):
    """
    Edit a final exam.

    Args:
        pk (int): FinalExam primary key.

    Returns:
        HttpResponse: Redirect on success or form page on error.
    """
    from app.services import FinalExamService
    
    final = get_object_or_404(FinalExam, pk=pk)
    if request.method == "POST":
        form = FinalExamForm(request.POST, instance=final)
        if form.is_valid():
            try:
                final_exam_service = FinalExamService()
                final_exam_service.update_final_exam(final, form.cleaned_data)
                messages.success(request, "Final actualizado correctamente.")
                return redirect("users:final-list")
            except Exception as e:
                messages.error(request, f"Error al actualizar final: {str(e)}")
    else:
        form = FinalExamForm(instance=final)
    return render(request, "users/final_form.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def final_delete(request, pk):
    """
    Delete a final exam after confirmation.

    Args:
        pk (int): FinalExam primary key.

    Returns:
        HttpResponse: Confirmation page (GET) or redirect (POST).
    """
    from app.services import FinalExamService
    
    final = get_object_or_404(FinalExam, pk=pk)
    if request.method == "POST":
        try:
            final_exam_service = FinalExamService()
            final_exam_service.delete_final_exam(final)
            messages.success(request, "Final eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar final: {str(e)}")
        return redirect("users:final-list")
    return render(request, "users/confirm_delete.html", {"object": final, "back": "users:final-list"})


@login_required
@user_passes_test(is_admin)
def assign_final_professors(request, pk):
    """
    Assign/remove professors for a final exam.

    Args:
        pk (int): FinalExam primary key.

    Returns:
        HttpResponse: Redirect to list after processing or form page (GET).
    """
    from app.services import AssignmentService
    
    final = get_object_or_404(FinalExam, pk=pk)
    
    if request.method == "POST":
        try:
            assignment_service = AssignmentService()
            selected_ids = request.POST.getlist("professors")
            result = assignment_service.update_final_professor_assignments(pk, selected_ids)
            
            if result['changes_made']:
                messages.success(request, result['message'])
            else:
                messages.info(request, result['message'])
        except Exception as e:
            messages.error(request, f"Error en las asignaciones: {str(e)}")
            
        return redirect("users:final-list")

    assignment_service = AssignmentService()
    professors = assignment_service.get_all_professors()
    return render(request, "users/assign_professors.html", {"final": final, "professors": professors})


# ------- Student Views -------
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
    from app.services import StudentService
    
    try:
        student_service = StudentService()
        dashboard_data = student_service.get_student_dashboard_data(request.user)
        return render(request, "users/student_dashboard.html", dashboard_data)
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
    from app.services import InscriptionService
    
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
        
        return redirect("users:student-dashboard")
    
    return render(request, "users/inscribe_confirm.html", {"subject": subject})


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
    from app.services import InscriptionService
    
    student = request.user.student
    final_exam = get_object_or_404(FinalExam, pk=final_exam_id, subject__career=student.career)
    
    # Check if student can inscribe (has REGULAR status)
    inscription_service = InscriptionService()
    try:
        inscription_service._validate_final_exam_inscription_requirements(student, final_exam)
    except Exception:
        # Redirect if cannot inscribe
        return redirect("users:student-dashboard")
    
    if request.method == "POST":
        try:
            inscription_service.inscribe_student_to_final_exam(student, final_exam)
            messages.success(request, "Inscripción al final realizada.")
        except Exception as e:
            messages.error(request, str(e))
        
        return redirect("users:student-dashboard")
    
    return render(request, "users/inscribe_confirm.html", {"final_exam": final_exam})


@login_required
def download_regular_certificate(request):
    """
    Generate and download a 'regular student' certificate as DOCX.
    """
    from app.services import CertificateService
    
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
        return redirect("users:student-dashboard")


# ------- Professor Views -------
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
    from app.services import ProfessorService
    
    try:
        professor_service = ProfessorService()
        dashboard_data = professor_service.get_professor_dashboard_data(request.user)
        return render(request, "users/professor_dashboard.html", dashboard_data)
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
    from app.services import GradeService
    
    professor = request.user.professor
    subject = get_object_or_404(Subject, code=subject_code, professors=professor)
    
    try:
        grade_service = GradeService()
        grades = grade_service.get_subject_grades_with_backfill(subject, professor)
        return render(request, "users/grade_list.html", {"grades": grades, "subject": subject})
    except Exception as e:
        messages.error(request, f"Error al obtener calificaciones: {str(e)}")
        return redirect("users:professor-dashboard")


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
    from app.services import GradeService
    
    grade = get_object_or_404(Grade, pk=pk)
    grade_service = GradeService()
    
    try:
        # Validate permissions through service
        grade_service.validate_grade_edit_permissions(grade, request.user.professor)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("users:professor-dashboard")

    if request.method == "POST":
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            try:
                grade_service.update_grade(grade, form.cleaned_data)
                return redirect("users:grade-list", subject_code=grade.subject.code)
            except Exception as e:
                messages.error(request, f"Error al actualizar calificación: {str(e)}")
    else:
        form = GradeForm(instance=grade)
    
    return render(request, "users/grade_form.html", {"form": form, "grade": grade})


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
    from app.services import ProfessorService
    
    try:
        professor_service = ProfessorService()
        inscriptions_data = professor_service.get_final_exam_inscriptions(final_exam_id, request.user.professor)
        return render(request, "users/professor_final_inscriptions.html", inscriptions_data)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("users:professor-dashboard")
