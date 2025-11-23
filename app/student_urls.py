"""URL patterns for student operations.

Student routes for:
- Dashboard
- Subject inscriptions
- Final exam inscriptions
"""

from django.urls import path

from app.views import student_views

urlpatterns = [
    # Student dashboard
    path("dashboard/", student_views.student_dashboard, name="student-dashboard"),
    # Inscriptions
    path(
        "subject/<str:subject_code>/inscribe/",
        student_views.subject_inscribe,
        name="subject-inscribe",
    ),
    path(
        "final/<int:final_exam_id>/inscribe/",
        student_views.final_exam_inscribe,
        name="final-inscribe",
    ),
]
