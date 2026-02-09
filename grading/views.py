from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from academics.models import Subject
from exceptions import ServiceError
from enrollments.models import FinalExam, FinalExamInscription
from grading.forms import GradeForm
from grading.models import Grade
from grading.services import GradeService
from users.mixins import ProfessorRequiredMixin


def _get_professor_and_object(request, model, pk_or_code, filter_field="professors"):
    """Helper to get professor and validate object access."""
    professor = request.user.professor
    filter_kwargs = {filter_field: professor}

    if isinstance(pk_or_code, int) or pk_or_code.isdigit():
        filter_kwargs["pk"] = pk_or_code
    else:
        filter_kwargs["code"] = pk_or_code

    obj = get_object_or_404(model, **filter_kwargs)
    return professor, obj


class SubjectGradeListView(ProfessorRequiredMixin, ListView):
    model = Grade
    template_name = "grading/professor/grade_list.html"
    context_object_name = "grades"

    def get_queryset(self):
        professor, subject = _get_professor_and_object(
            self.request, Subject, self.kwargs.get("code")
        )

        try:
            return GradeService.get_subject_grades_with_backfill(subject, professor)
        except ServiceError as e:
            messages.error(self.request, f"Error: {e.message}")
            return Grade.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor, subject = _get_professor_and_object(
            self.request, Subject, self.kwargs.get("code")
        )
        context["subject"] = subject
        context["professor"] = professor
        return context


class GradeUpdateView(ProfessorRequiredMixin, UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = "grading/professor/grade_form.html"

    def get_queryset(self):
        professor = self.request.user.professor
        return Grade.objects.filter(subject__professors=professor).select_related(
            "student__user", "subject"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["professor"] = self.request.user.professor
        return context

    def form_valid(self, form):
        grade = form.save(commit=False)
        professor = self.request.user.professor

        try:
            GradeService.validate_grade_edit_permissions(grade, professor)
            GradeService.update_grade(
                grade,
                promotion_grade=form.cleaned_data.get("promotion_grade"),
                final_grade=form.cleaned_data.get("final_grade"),
            )

            messages.success(
                self.request,
                f"Nota actualizada para {grade.student.user.get_full_name()}.",
            )
            return redirect("grading:subject-grades", code=grade.subject.code)

        except ServiceError as e:
            messages.error(self.request, f"Error: {e.message}")
            return self.form_invalid(form)


class FinalExamInscriptionsView(ProfessorRequiredMixin, ListView):
    model = FinalExamInscription
    template_name = "grading/professor/final_inscriptions.html"
    context_object_name = "inscriptions"

    def get_queryset(self):
        professor, final = _get_professor_and_object(
            self.request, FinalExam, self.kwargs.get("pk")
        )

        return (
            FinalExamInscription.objects.filter(final_exam=final)
            .select_related("student__user", "student__career")
            .order_by("student__user__last_name", "student__user__first_name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor, final = _get_professor_and_object(
            self.request, FinalExam, self.kwargs.get("pk")
        )
        context["final"] = final
        context["professor"] = professor
        return context
