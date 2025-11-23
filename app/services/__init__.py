"""
Services package: business logic layer.

Contains service classes that encapsulate business rules and coordinate
between repositories and external systems.
"""

from .user_management_service import UserManagementService, UserManagementServiceError

from .faculty_service import FacultyService, FacultyServiceError

from .career_service import CareerService, CareerServiceError

from .subject_service import SubjectService, SubjectServiceError

from .final_exam_service import FinalExamService, FinalExamServiceError

from .grade_service import GradeService, GradeServiceError

from .inscription_service import InscriptionService, InscriptionServiceError

from .professor_service import ProfessorService, ProfessorServiceError

from .student_service import StudentService, StudentServiceError

from .assignment_service import AssignmentService, AssignmentServiceError

from .authentication_service import AuthenticationService


__all__ = [
    # User Management
    "UserManagementService",
    "UserManagementServiceError",
    # Faculty Service
    "FacultyService",
    "FacultyServiceError",
    # Career Service
    "CareerService",
    "CareerServiceError",
    # Subject Service
    "SubjectService",
    "SubjectServiceError",
    # Final Exam Service
    "FinalExamService",
    "FinalExamServiceError",
    # Grade Service
    "GradeService",
    "GradeServiceError",
    # Inscription Service
    "InscriptionService",
    "InscriptionServiceError",
    # Professor Service
    "ProfessorService",
    "ProfessorServiceError",
    # Student Service
    "StudentService",
    "StudentServiceError",
    # Assignment Service
    "AssignmentService",
    "AssignmentServiceError",
    # Authentication Service
    "AuthenticationService",
]
