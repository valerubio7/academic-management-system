"""
Repositories package: persistence layer abstractions over Django ORM.

Exposes a typed BaseRepository and concrete repositories per aggregate.
Keep business logic in services; repositories are for data access only.
"""

from .base import BaseRepository
from .users import UserRepository
from .students import StudentRepository
from .professors import ProfessorRepository
from .administrators import AdministratorRepository
from .faculties import FacultyRepository
from .careers import CareerRepository
from .subjects import SubjectRepository
from .final_exams import FinalExamRepository
from .subject_inscriptions import SubjectInscriptionRepository
from .final_exam_inscriptions import FinalExamInscriptionRepository
from .grades import GradeRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "StudentRepository",
    "ProfessorRepository",
    "AdministratorRepository",
    "FacultyRepository",
    "CareerRepository",
    "SubjectRepository",
    "FinalExamRepository",
    "SubjectInscriptionRepository",
    "FinalExamInscriptionRepository",
    "GradeRepository",
]
