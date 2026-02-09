from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Base mixin for role-based access control."""

    required_role = None
    login_url = "/login/"

    def get_required_role(self):
        """Override in subclasses to return the required role."""
        if self.required_role is None:
            raise NotImplementedError("Subclasses must implement get_required_role")
        return self.required_role

    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role == self.get_required_role()
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("No tiene permisos para acceder a esta página.")


class AdministratorRequiredMixin(RoleRequiredMixin):
    def get_required_role(self):
        from users.models import CustomUser

        return CustomUser.Role.ADMIN


class ProfessorRequiredMixin(RoleRequiredMixin):
    def get_required_role(self):
        from users.models import CustomUser

        return CustomUser.Role.PROFESSOR


class StudentRequiredMixin(RoleRequiredMixin):
    def get_required_role(self):
        from users.models import CustomUser

        return CustomUser.Role.STUDENT


class ProfileRequiredMixin:
    """Mixin to ensure user has a specific profile configured."""

    profile_attr = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if self.profile_attr and not hasattr(request.user, self.profile_attr):
            role_name = self.profile_attr.capitalize()
            raise PermissionDenied(
                f"Tu perfil de {role_name.lower()} no está configurado. Contactá a un administrador."
            )

        return response


class StudentProfileRequiredMixin(StudentRequiredMixin, ProfileRequiredMixin):
    profile_attr = "student"


class ProfessorProfileRequiredMixin(ProfessorRequiredMixin, ProfileRequiredMixin):
    profile_attr = "professor"
