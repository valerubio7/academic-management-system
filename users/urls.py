from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    # Authentication
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    # Dashboards
    path(
        "admin/dashboard/", views.AdminDashboardView.as_view(), name="admin-dashboard"
    ),
    path(
        "professor/dashboard/",
        views.ProfessorDashboardView.as_view(),
        name="professor-dashboard",
    ),
    path(
        "student/dashboard/",
        views.StudentDashboardView.as_view(),
        name="student-dashboard",
    ),
    # User Management (Admin)
    path("admin/users/", views.UserListView.as_view(), name="user-list"),
    path("admin/users/create/", views.UserCreateView.as_view(), name="user-create"),
    path(
        "admin/users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user-edit"
    ),
    path(
        "admin/users/<int:pk>/delete/",
        views.UserDeleteView.as_view(),
        name="user-delete",
    ),
]
