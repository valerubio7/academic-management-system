"""URL patterns for admin operations.

Admin routes for CRUD operations on:
- Users
- Faculties
- Careers
- Subjects
- Final Exams
- Professor assignments
"""

from django.urls import path

from app.views import admin_views

urlpatterns = [
    # Admin dashboard
    path('dashboard/', admin_views.admin_dashboard, name='admin-dashboard'),
    
    # User management
    path('users/', admin_views.user_list, name='user-list'),
    path('users/create/', admin_views.user_create, name='user-create'),
    path('users/<int:pk>/edit/', admin_views.user_edit, name='user-edit'),
    path('users/<int:pk>/delete/', admin_views.user_delete, name='user-delete'),

    # Faculty management
    path('faculties/', admin_views.faculty_list, name='faculty-list'),
    path('faculties/create/', admin_views.faculty_create, name='faculty-create'),
    path('faculties/<str:code>/edit/', admin_views.faculty_edit, name='faculty-edit'),
    path('faculties/<str:code>/delete/', admin_views.faculty_delete, name='faculty-delete'),

    # Career management
    path('careers/', admin_views.career_list, name='career-list'),
    path('careers/create/', admin_views.career_create, name='career-create'),
    path('careers/<str:code>/edit/', admin_views.career_edit, name='career-edit'),
    path('careers/<str:code>/delete/', admin_views.career_delete, name='career-delete'),

    # Subject management
    path('subjects/', admin_views.subject_list, name='subject-list'),
    path('subjects/create/', admin_views.subject_create, name='subject-create'),
    path('subjects/<str:code>/edit/', admin_views.subject_edit, name='subject-edit'),
    path('subjects/<str:code>/delete/', admin_views.subject_delete, name='subject-delete'),
    path('subjects/<str:code>/assign-professors/', 
         admin_views.assign_subject_professors, 
         name='assign-subject-professors'),

    # Final exam management
    path('finals/', admin_views.final_list, name='final-list'),
    path('finals/create/', admin_views.final_create, name='final-create'),
    path('finals/<int:pk>/edit/', admin_views.final_edit, name='final-edit'),
    path('finals/<int:pk>/delete/', admin_views.final_delete, name='final-delete'),
    path('finals/<int:pk>/assign-professors/', admin_views.assign_final_professors, name='assign-final-professors'),
]