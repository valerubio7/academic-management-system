"""Admin views for the app.

Includes CRUD operations for:
- Users
- Faculties 
- Careers
- Subjects
- Final Exams
- Professor assignments
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from app.forms.admin_forms import CareerForm, FacultyForm, FinalExamForm, SubjectForm
from app.forms.user_forms import AdministratorProfileForm, ProfessorProfileForm, StudentProfileForm, UserForm
from app.models import (
    Career, Faculty, FinalExam, Subject, CustomUser
)
from app.repositories import (
    FacultyRepository, CareerRepository,
    SubjectRepository, FinalExamRepository
)
from app.services import UserManagementService


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
    return render(request, "app/admin/dashboard.html")


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """
    List all users with role-based filtering.

    Returns:
        HttpResponse: User list page with filtering and pagination.
    """
    filter_role = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('username')
    
    if filter_role and filter_role in [choice[0] for choice in CustomUser.Role.choices]:
        users = users.filter(role=filter_role)
    
    context = {
        'users': users,
        'current_filter': filter_role,
        'role_choices': CustomUser.Role.choices,
    }
    return render(request, "app/admin/user_list.html", context)


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """
    Create a new user.

    Returns:
        HttpResponse: User creation form or redirect on success.
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            service = UserManagementService()
            service.create_user_profile(user)
            messages.success(request, f"Usuario {user.username} creado exitosamente.")
            return redirect('app:user-list')
    else:
        form = UserForm()
    
    return render(request, "app/admin/user_form.html", {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    """
    Edit an existing user.

    Args:
        pk (int): User primary key.

    Returns:
        HttpResponse: User edit form or redirect on success.
    """
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = None
        
        # Get the appropriate profile form based on user role
        if user.role == CustomUser.Role.STUDENT and hasattr(user, 'student'):
            profile_form = StudentProfileForm(request.POST, instance=user.student)
        elif user.role == CustomUser.Role.PROFESSOR and hasattr(user, 'professor'):
            profile_form = ProfessorProfileForm(request.POST, instance=user.professor)
        elif user.role == CustomUser.Role.ADMIN and hasattr(user, 'administrator'):
            profile_form = AdministratorProfileForm(request.POST, instance=user.administrator)
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, f"Usuario {user.username} actualizado exitosamente.")
            return redirect('app:user-list')
    else:
        user_form = UserForm(instance=user)
        profile_form = None
        
        # Get the appropriate profile form based on user role
        if user.role == CustomUser.Role.STUDENT and hasattr(user, 'student'):
            profile_form = StudentProfileForm(instance=user.student)
        elif user.role == CustomUser.Role.PROFESSOR and hasattr(user, 'professor'):
            profile_form = ProfessorProfileForm(instance=user.professor)
        elif user.role == CustomUser.Role.ADMIN and hasattr(user, 'administrator'):
            profile_form = AdministratorProfileForm(instance=user.administrator)
    
    context = {
        'form': user_form,
        'profile_form': profile_form,
        'user': user,
        'action': 'Editar'
    }
    return render(request, "app/admin/user_form.html", context)


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    """
    Delete an existing user.

    Args:
        pk (int): User primary key.

    Returns:
        HttpResponse: Confirmation page or redirect on success.
    """
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"Usuario {username} eliminado exitosamente.")
        return redirect('app:user-list')
    
    return render(request, "app/admin/confirm_delete.html", {'object': user, 'back': 'app:user-list'})


# Faculty CRUD views
@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    """List all faculties."""
    repository = FacultyRepository()
    faculties = repository.list_all()
    return render(request, "app/admin/faculty_list.html", {'faculties': faculties})


@login_required
@user_passes_test(is_admin)
def faculty_create(request):
    """Create a new faculty."""
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f"Facultad {faculty.name} creada exitosamente.")
            return redirect('app:faculty-list')
    else:
        form = FacultyForm()
    
    return render(request, "app/admin/faculty_form.html", {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin)
def faculty_edit(request, code):
    """Edit an existing faculty."""
    faculty = get_object_or_404(Faculty, code=code)
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            faculty = form.save()
            messages.success(request, f"Facultad {faculty.name} actualizada exitosamente.")
            return redirect('app:faculty-list')
    else:
        form = FacultyForm(instance=faculty)
    
    return render(request, "app/admin/faculty_form.html", {'form': form, 'faculty': faculty, 'action': 'Editar'})


@login_required
@user_passes_test(is_admin)
def faculty_delete(request, code):
    """Delete an existing faculty."""
    faculty = get_object_or_404(Faculty, code=code)
    
    if request.method == 'POST':
        name = faculty.name
        faculty.delete()
        messages.success(request, f"Facultad {name} eliminada exitosamente.")
        return redirect('app:faculty-list')
    
    return render(request, "app/admin/confirm_delete.html", {'object': faculty, 'back': 'app:faculty-list'})


# Career CRUD views
@login_required
@user_passes_test(is_admin)
def career_list(request):
    """List all careers."""
    repository = CareerRepository()
    careers = repository.list_all()
    return render(request, "app/admin/career_list.html", {'careers': careers})


@login_required
@user_passes_test(is_admin)
def career_create(request):
    """Create a new career."""
    if request.method == 'POST':
        form = CareerForm(request.POST)
        if form.is_valid():
            career = form.save()
            messages.success(request, f"Carrera {career.name} creada exitosamente.")
            return redirect('app:career-list')
    else:
        form = CareerForm()
    
    return render(request, "app/admin/career_form.html", {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin)
def career_edit(request, code):
    """Edit an existing career."""
    career = get_object_or_404(Career, code=code)
    
    if request.method == 'POST':
        form = CareerForm(request.POST, instance=career)
        if form.is_valid():
            career = form.save()
            messages.success(request, f"Carrera {career.name} actualizada exitosamente.")
            return redirect('app:career-list')
    else:
        form = CareerForm(instance=career)
    
    return render(request, "app/admin/career_form.html", {'form': form, 'career': career, 'action': 'Editar'})


@login_required
@user_passes_test(is_admin)
def career_delete(request, code):
    """Delete an existing career."""
    career = get_object_or_404(Career, code=code)
    
    if request.method == 'POST':
        name = career.name
        career.delete()
        messages.success(request, f"Carrera {name} eliminada exitosamente.")
        return redirect('app:career-list')
    
    return render(request, "app/admin/confirm_delete.html", {'object': career, 'back': 'app:career-list'})


# Subject CRUD views
@login_required
@user_passes_test(is_admin)
def subject_list(request):
    """List all subjects."""
    repository = SubjectRepository()
    subjects = repository.list_all_with_career()
    return render(request, "app/admin/subject_list.html", {'subjects': subjects})


@login_required
@user_passes_test(is_admin)
def subject_create(request):
    """Create a new subject."""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Materia {subject.name} creada exitosamente.")
            return redirect('app:subject-list')
    else:
        form = SubjectForm()
    
    return render(request, "app/admin/subject_form.html", {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin)
def subject_edit(request, code):
    """Edit an existing subject."""
    subject = get_object_or_404(Subject, code=code)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"Materia {subject.name} actualizada exitosamente.")
            return redirect('app:subject-list')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, "app/admin/subject_form.html", {'form': form, 'subject': subject, 'action': 'Editar'})


@login_required
@user_passes_test(is_admin)
def subject_delete(request, code):
    """Delete an existing subject."""
    subject = get_object_or_404(Subject, code=code)
    
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f"Materia {name} eliminada exitosamente.")
        return redirect('app:subject-list')
    
    return render(request, "app/admin/confirm_delete.html", {'object': subject, 'back': 'app:subject-list'})


@login_required
@user_passes_test(is_admin)
def assign_subject_professors(request, code):
    """Assign professors to a subject."""
    subject = get_object_or_404(Subject, code=code)
    
    if request.method == 'POST':
        professor_ids = request.POST.getlist('professors')
        subject.professors.set(professor_ids)
        messages.success(request, f"Profesores asignados a {subject.name} exitosamente.")
        return redirect('app:subject-list')
    
    from app.models import Professor
    professors = Professor.objects.all()
    assigned_professors = subject.professors.all()
    
    context = {
        'subject': subject,
        'professors': professors,
        'assigned_professors': assigned_professors,
    }
    return render(request, "app/admin/assign_professors.html", context)


# Final Exam CRUD views
@login_required
@user_passes_test(is_admin)
def final_list(request):
    """List all final exams."""
    repository = FinalExamRepository()
    finals = repository.list_all_with_subject()
    return render(request, "app/admin/final_list.html", {'finals': finals})


@login_required
@user_passes_test(is_admin)
def final_create(request):
    """Create a new final exam."""
    if request.method == 'POST':
        form = FinalExamForm(request.POST)
        if form.is_valid():
            final = form.save()
            messages.success(request, f"Examen final creado exitosamente.")
            return redirect('app:final-list')
    else:
        form = FinalExamForm()
    
    return render(request, "app/admin/final_form.html", {'form': form, 'action': 'Crear'})


@login_required
@user_passes_test(is_admin)
def final_edit(request, pk):
    """Edit an existing final exam."""
    final = get_object_or_404(FinalExam, pk=pk)
    
    if request.method == 'POST':
        form = FinalExamForm(request.POST, instance=final)
        if form.is_valid():
            final = form.save()
            messages.success(request, f"Examen final actualizado exitosamente.")
            return redirect('app:final-list')
    else:
        form = FinalExamForm(instance=final)
    
    return render(request, "app/admin/final_form.html", {'form': form, 'final': final, 'action': 'Editar'})


@login_required
@user_passes_test(is_admin)
def final_delete(request, pk):
    """Delete an existing final exam."""
    final = get_object_or_404(FinalExam, pk=pk)
    
    if request.method == 'POST':
        final.delete()
        messages.success(request, f"Examen final eliminado exitosamente.")
        return redirect('app:final-list')
    
    return render(request, "app/admin/confirm_delete.html", {'object': final, 'back': 'app:final-list'})


@login_required
@user_passes_test(is_admin)
def assign_final_professors(request, pk):
    """Assign professors to a final exam."""
    final = get_object_or_404(FinalExam, pk=pk)
    
    if request.method == 'POST':
        professor_ids = request.POST.getlist('professors')
        final.professors.set(professor_ids)
        messages.success(request, f"Profesores asignados al examen final exitosamente.")
        return redirect('app:final-list')
    
    from app.models import Professor
    professors = Professor.objects.all()
    assigned_professors = final.professors.all()
    
    context = {
        'final': final,
        'professors': professors,
        'assigned_professors': assigned_professors,
    }
    return render(request, "app/admin/assign_professors.html", context)
