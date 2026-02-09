from django.urls import path

from grading import views

app_name = "grading"

urlpatterns = [
    path(
        "professor/subjects/<str:code>/grades/",
        views.SubjectGradeListView.as_view(),
        name="subject-grades",
    ),
    path(
        "professor/grades/<int:pk>/edit/",
        views.GradeUpdateView.as_view(),
        name="grade-edit",
    ),
    path(
        "professor/finals/<int:pk>/inscriptions/",
        views.FinalExamInscriptionsView.as_view(),
        name="final-inscriptions",
    ),
]
