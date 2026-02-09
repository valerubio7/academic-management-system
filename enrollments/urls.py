from django.urls import path
from enrollments import views

app_name = "enrollments"

urlpatterns = [
    # Final Exam Management (Admin)
    path("admin/finals/", views.FinalExamListView.as_view(), name="final-list"),
    path(
        "admin/finals/create/", views.FinalExamCreateView.as_view(), name="final-create"
    ),
    path(
        "admin/finals/<int:pk>/edit/",
        views.FinalExamUpdateView.as_view(),
        name="final-edit",
    ),
    path(
        "admin/finals/<int:pk>/delete/",
        views.FinalExamDeleteView.as_view(),
        name="final-delete",
    ),
    path(
        "admin/finals/<int:pk>/assign-professors/",
        views.AssignFinalProfessorsView.as_view(),
        name="final-assign-professors",
    ),
    # Student Enrollment Views
    path(
        "student/subjects/",
        views.AvailableSubjectsView.as_view(),
        name="available-subjects",
    ),
    path(
        "student/subjects/<str:code>/enroll/",
        views.SubjectEnrollView.as_view(),
        name="subject-enroll",
    ),
    path(
        "student/finals/", views.AvailableFinalsView.as_view(), name="available-finals"
    ),
    path(
        "student/finals/<int:pk>/enroll/",
        views.FinalEnrollView.as_view(),
        name="final-enroll",
    ),
    path(
        "student/my-enrollments/",
        views.MyEnrollmentsView.as_view(),
        name="my-enrollments",
    ),
]
