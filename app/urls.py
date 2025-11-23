"""URL patterns for the app.

Sections:
- Auth: login/logout routes.
- Admin: CRUD for users, faculties, careers, subjects, finals, and assignments.
- Student: dashboard, subject/final inscriptions.
- Professor: dashboard, grade management, final inscriptions.

Notes:
    Namespaced via app_name = "app" to enable reverse('app:<name>').
    Access control is enforced in views (role-based decorators or checks).
"""

from django.urls import path, include

app_name = "app"

urlpatterns = [
    # Authentication routes
    path("", include("app.auth_urls")),
    # Admin routes
    path("admin/", include("app.admin_urls")),
    # Student routes
    path("student/", include("app.student_urls")),
    # Professor routes
    path("professor/", include("app.professor_urls")),
]
