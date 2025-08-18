"""URL patterns for the Users app.

Sections:
- Admin: CRUD for users, faculties, careers, subjects, finals, and assignments.
- Student: dashboard, subject/final inscriptions, certificates.
- Professor: dashboard, grade management, final inscriptions.

Notes:
    Namespaced via app_name = "users" to enable reverse('users:<name>').
    Access control is enforced in views (role-based decorators or checks).
"""

from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Admin
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/users/', views.user_list, name='user-list'),
    path('admin/users/create/', views.user_create, name='user-create'),
    path('admin/users/<int:pk>/edit/', views.user_edit, name='user-edit'),
    path('admin/users/<int:pk>/delete/', views.user_delete, name='user-delete'),

    path('admin/faculties/', views.faculty_list, name='faculty-list'),
    path('admin/faculties/create/', views.faculty_create, name='faculty-create'),
    path('admin/faculties/<str:code>/edit/', views.faculty_edit, name='faculty-edit'),
    path('admin/faculties/<str:code>/delete/', views.faculty_delete, name='faculty-delete'),

    path('admin/careers/', views.career_list, name='career-list'),
    path('admin/careers/create/', views.career_create, name='career-create'),
    path('admin/careers/<str:code>/edit/', views.career_edit, name='career-edit'),
    path('admin/careers/<str:code>/delete/', views.career_delete, name='career-delete'),

    path('admin/subjects/', views.subject_list, name='subject-list'),
    path('admin/subjects/create/', views.subject_create, name='subject-create'),
    path('admin/subjects/<str:code>/edit/', views.subject_edit, name='subject-edit'),
    path('admin/subjects/<str:code>/delete/', views.subject_delete, name='subject-delete'),
    path('admin/subjects/<str:code>/assign-professors/', views.assign_subject_professors, name='assign-subject-professors'),

    path('admin/finals/', views.final_list, name='final-list'),
    path('admin/finals/create/', views.final_create, name='final-create'),
    path('admin/finals/<int:pk>/edit/', views.final_edit, name='final-edit'),
    path('admin/finals/<int:pk>/delete/', views.final_delete, name='final-delete'),
    path('admin/finals/<int:pk>/assign-professors/', views.assign_final_professors, name='assign-final-professors'),

    # Student
    path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    path('student/subject/<str:subject_code>/inscribe/', views.subject_inscribe, name='subject-inscribe'),
    path('student/final/<int:final_exam_id>/inscribe/', views.final_exam_inscribe, name='final-inscribe'),
    path('student/certificate/regular/', views.download_regular_certificate, name='student-regular-certificate'),

    # Professor
    path('professor/dashboard/', views.professor_dashboard, name='professor-dashboard'),
    path('professor/grades/<str:subject_code>/', views.grade_list, name='grade-list'),
    path('professor/grade/<int:pk>/edit/', views.grade_edit, name='grade-edit'),
    path('professor/final/<int:final_exam_id>/inscriptions/',views.professor_final_inscriptions, name='professor-final-inscriptions')
]
