from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from academics.models import Subject
from exceptions import ServiceError
from enrollments.forms import FinalExamForm
from enrollments.models import FinalExam, FinalExamInscription, SubjectInscription
from enrollments.services import EnrollmentService
from users.mixins import AdministratorRequiredMixin, StudentRequiredMixin
from users.models import Professor
from users.services import AssignmentService


# ============================================================================
# FINAL EXAM CRUD VIEWS (Admin)
# ============================================================================


class FinalExamListView(AdministratorRequiredMixin, ListView):
    model = FinalExam
    template_name = "enrollments/admin/final_list.html"
    context_object_name = "finals"

    def get_queryset(self):
        return FinalExam.objects.select_related("subject__career").order_by("-date")


class FinalExamCreateView(AdministratorRequiredMixin, CreateView):
    model = FinalExam
    form_class = FinalExamForm
    template_name = "enrollments/admin/final_form.html"
    success_url = reverse_lazy("enrollments:final-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Crear"
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Examen final creado exitosamente.")
        return redirect(self.success_url)


class FinalExamUpdateView(AdministratorRequiredMixin, UpdateView):
    model = FinalExam
    form_class = FinalExamForm
    template_name = "enrollments/admin/final_form.html"
    success_url = reverse_lazy("enrollments:final-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Editar"
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Examen final actualizado exitosamente.")
        return redirect(self.success_url)


class FinalExamDeleteView(AdministratorRequiredMixin, DeleteView):
    model = FinalExam
    template_name = "enrollments/admin/confirm_delete.html"
    success_url = reverse_lazy("enrollments:final-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back"] = "enrollments:final-list"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Examen final eliminado exitosamente.")
        return super().form_valid(form)


# ============================================================================
# PROFESSOR ASSIGNMENT FOR FINALS
# ============================================================================


class AssignFinalProfessorsView(AdministratorRequiredMixin, TemplateView):
    template_name = "enrollments/admin/assign_professors.html"

    def _get_final(self):
        return get_object_or_404(FinalExam, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        final = self._get_final()
        context["final"] = final
        context["professors"] = Professor.objects.select_related("user").all()
        context["assigned_professors"] = final.professors.all()
        return context

    def post(self, request, *args, **kwargs):
        final = self._get_final()
        professor_ids = request.POST.getlist("professors")

        try:
            result = AssignmentService.update_final_professor_assignments(
                final, professor_ids
            )
            messages.success(request, result["message"])
        except Exception as e:
            messages.error(request, f"Error al asignar profesores: {str(e)}")

        return redirect("enrollments:final-list")


# ============================================================================
# STUDENT ENROLLMENT VIEWS
# ============================================================================


class _EnrollmentViewMixin:
    """Base mixin for enrollment confirmation and processing views."""

    def _handle_enrollment_get(
        self, request, enrollment_obj, can_enroll_func, template, context_key
    ):
        """Handle GET request for enrollment confirmation."""
        student = request.user.student
        can_enroll, reason = can_enroll_func(student, enrollment_obj)
        return render(
            request,
            template,
            {context_key: enrollment_obj, "can_enroll": can_enroll, "reason": reason},
        )

    def _handle_enrollment_post(
        self, request, enrollment_obj, enroll_func, success_message
    ):
        """Handle POST request for enrollment processing."""
        student = request.user.student
        try:
            enroll_func(student, enrollment_obj)
            messages.success(request, success_message)
        except ServiceError as e:
            messages.error(request, f"Error en la inscripción: {e.message}")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
        return redirect("users:student-dashboard")


class AvailableSubjectsView(StudentRequiredMixin, ListView):
    model = Subject
    template_name = "enrollments/student/available_subjects.html"
    context_object_name = "subjects"
    paginate_by = 20

    def get_queryset(self):
        student = self.request.user.student
        return EnrollmentService.get_available_subjects_for_student(student)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.request.user.student
        return context


class SubjectEnrollView(StudentRequiredMixin, _EnrollmentViewMixin, View):
    def get(self, request, code):
        subject = get_object_or_404(Subject, code=code)
        return self._handle_enrollment_get(
            request,
            subject,
            EnrollmentService.can_enroll_in_subject,
            "enrollments/student/subject_enroll_confirm.html",
            "subject",
        )

    def post(self, request, code):
        subject = get_object_or_404(Subject, code=code)
        return self._handle_enrollment_post(
            request,
            subject,
            EnrollmentService.enroll_in_subject,
            f"Te inscribiste exitosamente en {subject.name}.",
        )


class AvailableFinalsView(StudentRequiredMixin, ListView):
    model = FinalExam
    template_name = "enrollments/student/available_finals.html"
    context_object_name = "finals"
    paginate_by = 20

    def get_queryset(self):
        student = self.request.user.student
        return EnrollmentService.get_available_finals_for_student(student)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = self.request.user.student
        return context


class FinalEnrollView(StudentRequiredMixin, _EnrollmentViewMixin, View):
    def get(self, request, pk):
        final = get_object_or_404(FinalExam, pk=pk)
        return self._handle_enrollment_get(
            request,
            final,
            EnrollmentService.can_enroll_in_final,
            "enrollments/student/final_enroll_confirm.html",
            "final",
        )

    def post(self, request, pk):
        final = get_object_or_404(FinalExam, pk=pk)
        return self._handle_enrollment_post(
            request,
            final,
            EnrollmentService.enroll_in_final,
            f"Te inscribiste exitosamente en el final de {final.subject.name}.",
        )


class MyEnrollmentsView(StudentRequiredMixin, TemplateView):
    template_name = "enrollments/student/my_enrollments.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student

        # Get subject inscriptions
        subject_inscriptions = (
            SubjectInscription.objects.filter(student=student)
            .select_related("subject__career")
            .order_by("-inscription_date")
        )

        # Get final exam inscriptions
        final_inscriptions = (
            FinalExamInscription.objects.filter(student=student)
            .select_related("final_exam__subject")
            .order_by("-inscription_date")
        )

        context["student"] = student
        context["subject_inscriptions"] = subject_inscriptions
        context["final_inscriptions"] = final_inscriptions

        return context
