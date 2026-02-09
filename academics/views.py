from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from academics.forms import CareerForm, FacultyForm, SubjectForm
from academics.models import Career, Faculty, Subject
from users.mixins import AdministratorRequiredMixin
from users.models import Professor
from users.services import AssignmentService


# ============================================================================
# BASE CRUD VIEWS (DRY)
# ============================================================================


class _BaseCRUDMixin:
    """Base mixin for common CRUD functionality."""

    entity_name = None  # Debe ser sobreescrito por subclases

    def get_success_message(self, action, obj):
        """Generate success message for CRUD operations."""
        return f"{self.entity_name} {obj.name} {action} exitosamente."


class BaseCreateView(_BaseCRUDMixin, AdministratorRequiredMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Crear"
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, self.get_success_message("creada", form.instance)
        )
        return redirect(self.success_url)


class BaseUpdateView(_BaseCRUDMixin, AdministratorRequiredMixin, UpdateView):
    slug_field = "code"
    slug_url_kwarg = "code"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Editar"
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, self.get_success_message("actualizada", form.instance)
        )
        return redirect(self.success_url)


class BaseDeleteView(_BaseCRUDMixin, AdministratorRequiredMixin, DeleteView):
    template_name = "academics/admin/confirm_delete.html"
    slug_field = "code"
    slug_url_kwarg = "code"
    back_url = None  # Debe ser sobreescrito

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back"] = self.back_url
        return context

    def form_valid(self, form):
        name = self.object.name
        messages.success(
            self.request, self.get_success_message("eliminada", self.object)
        )
        return super().form_valid(form)


# ============================================================================
# FACULTY CRUD VIEWS
# ============================================================================


class FacultyListView(AdministratorRequiredMixin, ListView):
    model = Faculty
    template_name = "academics/admin/faculty_list.html"
    context_object_name = "faculties"
    ordering = ["name"]


class FacultyCreateView(BaseCreateView):
    model = Faculty
    form_class = FacultyForm
    template_name = "academics/admin/faculty_form.html"
    success_url = reverse_lazy("academics:faculty-list")
    entity_name = "Facultad"


class FacultyUpdateView(BaseUpdateView):
    model = Faculty
    form_class = FacultyForm
    template_name = "academics/admin/faculty_form.html"
    success_url = reverse_lazy("academics:faculty-list")
    entity_name = "Facultad"


class FacultyDeleteView(BaseDeleteView):
    model = Faculty
    success_url = reverse_lazy("academics:faculty-list")
    back_url = "academics:faculty-list"
    entity_name = "Facultad"


# ============================================================================
# CAREER CRUD VIEWS
# ============================================================================


class CareerListView(AdministratorRequiredMixin, ListView):
    model = Career
    template_name = "academics/admin/career_list.html"
    context_object_name = "careers"
    ordering = ["name"]

    def get_queryset(self):
        return Career.objects.select_related("faculty").order_by("name")


class CareerCreateView(BaseCreateView):
    model = Career
    form_class = CareerForm
    template_name = "academics/admin/career_form.html"
    success_url = reverse_lazy("academics:career-list")
    entity_name = "Carrera"


class CareerUpdateView(BaseUpdateView):
    model = Career
    form_class = CareerForm
    template_name = "academics/admin/career_form.html"
    success_url = reverse_lazy("academics:career-list")
    entity_name = "Carrera"


class CareerDeleteView(BaseDeleteView):
    model = Career
    success_url = reverse_lazy("academics:career-list")
    back_url = "academics:career-list"
    entity_name = "Carrera"


# ============================================================================
# SUBJECT CRUD VIEWS
# ============================================================================


class SubjectListView(AdministratorRequiredMixin, ListView):
    model = Subject
    template_name = "academics/admin/subject_list.html"
    context_object_name = "subjects"

    def get_queryset(self):
        return Subject.objects.select_related("career__faculty").order_by("name")


class SubjectCreateView(BaseCreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "academics/admin/subject_form.html"
    success_url = reverse_lazy("academics:subject-list")
    entity_name = "Materia"


class SubjectUpdateView(BaseUpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "academics/admin/subject_form.html"
    success_url = reverse_lazy("academics:subject-list")
    entity_name = "Materia"


class SubjectDeleteView(BaseDeleteView):
    model = Subject
    success_url = reverse_lazy("academics:subject-list")
    back_url = "academics:subject-list"
    entity_name = "Materia"


# ============================================================================
# PROFESSOR ASSIGNMENT VIEWS
# ============================================================================


class AssignSubjectProfessorsView(AdministratorRequiredMixin, TemplateView):
    template_name = "academics/admin/assign_professors.html"

    def _get_subject(self):
        return get_object_or_404(Subject, code=self.kwargs.get("code"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject = self._get_subject()
        context["subject"] = subject
        context["professors"] = Professor.objects.select_related("user").all()
        context["assigned_professors"] = subject.professors.all()
        return context

    def post(self, request, *args, **kwargs):
        subject = self._get_subject()
        professor_ids = request.POST.getlist("professors")

        try:
            result = AssignmentService.update_subject_professor_assignments(
                subject, professor_ids
            )
            messages.success(request, result["message"])
        except Exception as e:
            messages.error(request, f"Error al asignar profesores: {str(e)}")

        return redirect("academics:subject-list")
