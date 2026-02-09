from django.urls import path
from academics import views

app_name = "academics"

urlpatterns = [
    # Faculty Management (Admin)
    path("admin/faculties/", views.FacultyListView.as_view(), name="faculty-list"),
    path(
        "admin/faculties/create/",
        views.FacultyCreateView.as_view(),
        name="faculty-create",
    ),
    path(
        "admin/faculties/<str:code>/edit/",
        views.FacultyUpdateView.as_view(),
        name="faculty-edit",
    ),
    path(
        "admin/faculties/<str:code>/delete/",
        views.FacultyDeleteView.as_view(),
        name="faculty-delete",
    ),
    # Career Management (Admin)
    path("admin/careers/", views.CareerListView.as_view(), name="career-list"),
    path(
        "admin/careers/create/", views.CareerCreateView.as_view(), name="career-create"
    ),
    path(
        "admin/careers/<str:code>/edit/",
        views.CareerUpdateView.as_view(),
        name="career-edit",
    ),
    path(
        "admin/careers/<str:code>/delete/",
        views.CareerDeleteView.as_view(),
        name="career-delete",
    ),
    # Subject Management (Admin)
    path("admin/subjects/", views.SubjectListView.as_view(), name="subject-list"),
    path(
        "admin/subjects/create/",
        views.SubjectCreateView.as_view(),
        name="subject-create",
    ),
    path(
        "admin/subjects/<str:code>/edit/",
        views.SubjectUpdateView.as_view(),
        name="subject-edit",
    ),
    path(
        "admin/subjects/<str:code>/delete/",
        views.SubjectDeleteView.as_view(),
        name="subject-delete",
    ),
    path(
        "admin/subjects/<str:code>/assign-professors/",
        views.AssignSubjectProfessorsView.as_view(),
        name="subject-assign-professors",
    ),
]
