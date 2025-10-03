"""URL patterns for professor operations.

Professor routes for:
- Dashboard
- Grade management
- Final exam inscription management
"""

from django.urls import path

from app.views import professor_views

urlpatterns = [
    # Professor dashboard
    path('dashboard/', professor_views.professor_dashboard, name='professor-dashboard'),
    
    # Grade management
    path('grades/<str:subject_code>/', professor_views.grade_list, name='grade-list'),
    path('grade/<int:pk>/edit/', professor_views.grade_edit, name='grade-edit'),
    
    # Final exam management
    path('final/<int:final_exam_id>/inscriptions/', 
         professor_views.professor_final_inscriptions, 
         name='professor-final-inscriptions'),
]