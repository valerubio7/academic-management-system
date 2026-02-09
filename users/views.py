from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from users.forms import (
    AdministratorProfileForm,
    LoginForm,
    ProfessorProfileForm,
    StudentProfileForm,
    UserForm,
)
from users.mixins import (
    AdministratorRequiredMixin,
    ProfessorRequiredMixin,
    StudentRequiredMixin,
)
from users.models import CustomUser
from users.services import UserService


def _ensure_superuser_role(user):
    """Ensure superusers have administrator role."""
    if user.is_superuser and user.role != CustomUser.Role.ADMIN:
        user.role = CustomUser.Role.ADMIN
        user.save(update_fields=["role"])


def _get_dashboard_by_role(user):
    """Return dashboard URL based on user role."""
    role_dashboards = {
        CustomUser.Role.STUDENT: "users:student-dashboard",
        CustomUser.Role.PROFESSOR: "users:professor-dashboard",
        CustomUser.Role.ADMIN: "users:admin-dashboard",
    }
    return role_dashboards.get(user.role, "home")


def user_login(request):
    if request.user.is_authenticated:
        _ensure_superuser_role(request.user)
        return redirect(_get_dashboard_by_role(request.user))

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                _ensure_superuser_role(user)

                next_url = request.GET.get("next")
                return (
                    redirect(next_url)
                    if next_url
                    else redirect(_get_dashboard_by_role(user))
                )

            form.add_error(None, "Usuario o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("home")


class AdminDashboardView(AdministratorRequiredMixin, TemplateView):
    template_name = "users/admin_dashboard.html"


class ProfessorDashboardView(ProfessorRequiredMixin, TemplateView):
    template_name = "users/professor_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor = self.request.user.professor

        from academics.models import Subject
        from enrollments.models import FinalExam

        assigned_subjects = (
            Subject.objects.filter(professors=professor)
            .select_related("career__faculty")
            .order_by("career__name", "year", "name")
        )

        assigned_finals = (
            FinalExam.objects.filter(professors=professor)
            .select_related("subject__career")
            .order_by("-date")[:10]
        )

        context["professor"] = professor
        context["assigned_subjects"] = assigned_subjects
        context["assigned_finals"] = assigned_finals
        context["subjects_count"] = assigned_subjects.count()

        return context


class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = "users/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student

        from enrollments.models import SubjectInscription, FinalExamInscription
        from grading.models import Grade

        enrolled_subjects = (
            SubjectInscription.objects.filter(student=student)
            .select_related("subject__career")
            .order_by("subject__year", "subject__name")
        )

        grades = Grade.objects.filter(student=student).select_related("subject")
        grades_dict = {grade.subject.code: grade for grade in grades}

        subjects_with_grades = [
            {
                "inscription": inscription,
                "grade": grades_dict.get(inscription.subject.code),
            }
            for inscription in enrolled_subjects
        ]

        final_inscriptions = (
            FinalExamInscription.objects.filter(student=student)
            .select_related("final_exam__subject")
            .order_by("-final_exam__date")[:5]
        )

        context["student"] = student
        context["subjects_with_grades"] = subjects_with_grades
        context["final_inscriptions"] = final_inscriptions
        context["enrolled_count"] = enrolled_subjects.count()

        return context


# ============================================================================
# ADMIN VIEWS - User Management CRUD
# ============================================================================


class UserListView(AdministratorRequiredMixin, ListView):
    model = CustomUser
    template_name = "users/admin/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by("username")
        filter_role = self.request.GET.get("role", "")

        if filter_role and filter_role in [
            choice[0] for choice in CustomUser.Role.choices
        ]:
            queryset = queryset.filter(role=filter_role)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_filter"] = self.request.GET.get("role", "")
        context["role_choices"] = CustomUser.Role.choices
        return context


class UserCreateView(AdministratorRequiredMixin, CreateView):
    model = CustomUser
    form_class = UserForm
    template_name = "users/admin/user_form.html"
    success_url = reverse_lazy("users:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Crear"
        return context

    def form_valid(self, form):
        user = form.save()

        try:
            UserService.create_user_profile(user)
            messages.success(
                self.request, f"Usuario {user.username} creado exitosamente."
            )
        except Exception as e:
            messages.warning(
                self.request,
                f"Usuario creado pero hubo un error al crear el perfil: {str(e)}",
            )

        return super().form_valid(form)


class UserUpdateView(AdministratorRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserForm
    template_name = "users/admin/user_form.html"
    success_url = reverse_lazy("users:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Editar"
        user = self.get_object()

        if user.role == CustomUser.Role.STUDENT and hasattr(user, "student"):
            context["profile_form"] = StudentProfileForm(instance=user.student)
        elif user.role == CustomUser.Role.PROFESSOR and hasattr(user, "professor"):
            context["profile_form"] = ProfessorProfileForm(instance=user.professor)
        elif user.role == CustomUser.Role.ADMIN and hasattr(user, "administrator"):
            context["profile_form"] = AdministratorProfileForm(
                instance=user.administrator
            )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = UserForm(request.POST, instance=self.object)
        profile_form = self._get_profile_form(request.POST)

        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(
                request, f"Usuario {self.object.username} actualizado exitosamente."
            )
            return redirect(self.success_url)

        return self.render_to_response(
            self.get_context_data(form=user_form, profile_form=profile_form)
        )

    def _get_profile_form(self, data=None):
        """Get appropriate profile form based on user role."""
        role_forms = {
            CustomUser.Role.STUDENT: (StudentProfileForm, "student"),
            CustomUser.Role.PROFESSOR: (ProfessorProfileForm, "professor"),
            CustomUser.Role.ADMIN: (AdministratorProfileForm, "administrator"),
        }

        form_class, profile_attr = role_forms.get(self.object.role, (None, None))
        if form_class and hasattr(self.object, profile_attr):
            return form_class(data, instance=getattr(self.object, profile_attr))
        return None


class UserDeleteView(AdministratorRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "users/admin/confirm_delete.html"
    success_url = reverse_lazy("users:user-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back"] = "users:user-list"
        return context

    def form_valid(self, form):
        username = self.object.username
        messages.success(self.request, f"Usuario {username} eliminado exitosamente.")
        return super().form_valid(form)
