"""Forms package for the app."""

from .auth_forms import LoginForm
from .user_forms import UserForm, StudentProfileForm, ProfessorProfileForm, AdministratorProfileForm
from .admin_forms import FacultyForm, CareerForm, SubjectForm, FinalExamForm
from .grade_forms import GradeForm