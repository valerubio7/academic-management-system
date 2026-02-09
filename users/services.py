from datetime import date

from django.contrib.auth.hashers import make_password
from django.db import transaction

from exceptions import ServiceError


class UserService:
    """Manages users and their role-specific profiles."""

    PROFILE_DEFAULTS = {
        "student": {
            "id_prefix": "STU",
            "id_field": "student_id",
            "model_name": "Student",
            "extra_defaults": {"enrollment_date": lambda: date.today()},
        },
        "professor": {
            "id_prefix": "PROF",
            "id_field": "professor_id",
            "model_name": "Professor",
            "extra_defaults": {
                "degree": "Sin especificar",
                "category": "auxiliar",
                "hire_date": lambda: date.today(),
            },
        },
        "administrator": {
            "id_prefix": "ADM",
            "id_field": "administrator_id",
            "model_name": "Administrator",
            "extra_defaults": {
                "position": "Administrador",
                "hire_date": lambda: date.today(),
            },
        },
    }

    @staticmethod
    def _hash_password(user_data):
        """Hash password if present in user data."""
        if "password" in user_data and user_data["password"]:
            user_data["password"] = make_password(user_data["password"])

    @staticmethod
    def _create_user_with_role(role):
        """Create CustomUser with specified role."""
        from users.models import CustomUser

        def create(user_data):
            UserService._hash_password(user_data)
            user_data["role"] = role
            return CustomUser.objects.create(**user_data)

        return create

    @staticmethod
    def _apply_defaults(profile_data, user_id, role):
        """Apply default values to profile data."""
        config = UserService.PROFILE_DEFAULTS[role]

        if config["id_field"] not in profile_data:
            profile_data[config["id_field"]] = f"{config['id_prefix']}{user_id:05d}"

        for field, value in config["extra_defaults"].items():
            if field not in profile_data:
                profile_data[field] = value() if callable(value) else value

    @staticmethod
    @transaction.atomic
    def _create_user_with_profile(user_data, profile_data, role):
        """Generic method to create user with profile."""
        from users.models import CustomUser, Student, Professor, Administrator

        profile_models = {
            CustomUser.Role.STUDENT: Student,
            CustomUser.Role.PROFESSOR: Professor,
            CustomUser.Role.ADMIN: Administrator,
        }

        try:
            create_user = UserService._create_user_with_role(role)
            user = create_user(user_data)

            if profile_data is None:
                profile_data = {}

            UserService._apply_defaults(profile_data, user.id, role)

            profile_model = profile_models[role]
            profile_model.objects.create(user=user, **profile_data)

            return user

        except Exception as e:
            raise ServiceError(
                service="UserService",
                operation=f"create_{role}",
                message=f"Failed to create {role}: {str(e)}",
                original_exception=e,
            )

    @staticmethod
    @transaction.atomic
    def create_student(user_data: dict, student_data: dict = None):
        from users.models import CustomUser

        return UserService._create_user_with_profile(
            user_data, student_data, CustomUser.Role.STUDENT
        )

    @staticmethod
    @transaction.atomic
    def create_professor(user_data: dict, professor_data: dict = None):
        from users.models import CustomUser

        return UserService._create_user_with_profile(
            user_data, professor_data, CustomUser.Role.PROFESSOR
        )

    @staticmethod
    @transaction.atomic
    def create_administrator(user_data: dict, admin_data: dict = None):
        from users.models import CustomUser

        return UserService._create_user_with_profile(
            user_data, admin_data, CustomUser.Role.ADMIN
        )

    @staticmethod
    @transaction.atomic
    def create_user_profile(user):
        """Create role-specific profile for an existing user."""
        from users.models import Student, Professor, Administrator

        profile_models = {
            "student": (
                Student,
                {"student_id": f"STU{user.id:05d}", "enrollment_date": date.today()},
            ),
            "professor": (
                Professor,
                {
                    "professor_id": f"PROF{user.id:05d}",
                    "degree": "Sin especificar",
                    "category": "auxiliar",
                    "hire_date": date.today(),
                },
            ),
            "administrator": (
                Administrator,
                {
                    "administrator_id": f"ADM{user.id:05d}",
                    "position": "Administrador",
                    "hire_date": date.today(),
                },
            ),
        }

        try:
            model_class, defaults = profile_models.get(user.role, (None, {}))
            if model_class:
                return model_class.objects.create(user=user, **defaults)
            return None

        except Exception as e:
            raise ServiceError(
                service="UserService",
                operation="create_user_profile",
                message=f"Failed to create user profile: {str(e)}",
                original_exception=e,
            )

    @staticmethod
    @transaction.atomic
    def update_user_with_profile(user, user_data: dict, profile_data: dict = None):
        """Update user and optionally their profile data atomically."""
        try:
            if "password" in user_data:
                if user_data["password"]:
                    user_data["password"] = make_password(user_data["password"])
                else:
                    del user_data["password"]

            for field, value in user_data.items():
                setattr(user, field, value)
            user.save()

            if profile_data:
                profile_attrs = {
                    "student": "student",
                    "professor": "professor",
                    "administrator": "administrator",
                }
                profile = getattr(user, profile_attrs.get(user.role, ""), None)

                if profile:
                    for field, value in profile_data.items():
                        setattr(profile, field, value)
                    profile.save()

            return user

        except Exception as e:
            raise ServiceError(
                service="UserService",
                operation="update_user_with_profile",
                message=f"Failed to update user: {str(e)}",
                original_exception=e,
            )


class AssignmentService:
    """Manages professor assignments to subjects and final exams."""

    @staticmethod
    @transaction.atomic
    def _update_assignments(entity, selected_ids: list[str], entity_type: str) -> dict:
        """Generic method to update M2M assignments."""
        try:
            selected_ids_set = set(pid for pid in selected_ids if pid)
            current_ids = set(entity.professors.values_list("pk", flat=True))

            to_add = selected_ids_set - current_ids
            to_remove = current_ids - selected_ids_set

            changes_made = False
            if to_add or to_remove:
                if to_add:
                    entity.professors.add(*to_add)
                if to_remove:
                    entity.professors.remove(*to_remove)
                changes_made = True

            message = (
                f"Asignaciones{' del final' if entity_type == 'final' else ''} actualizadas correctamente."
                if changes_made
                else "No hubo cambios en las asignaciones."
            )

            return {"success": True, "changes_made": changes_made, "message": message}

        except Exception as e:
            raise ServiceError(
                service="AssignmentService",
                operation=f"update_{entity_type}_assignments",
                message=f"Failed to update {entity_type} assignments: {str(e)}",
                original_exception=e,
            )

    @staticmethod
    @transaction.atomic
    def update_subject_professor_assignments(
        subject, selected_professor_ids: list[str]
    ) -> dict:
        return AssignmentService._update_assignments(
            subject, selected_professor_ids, "subject"
        )

    @staticmethod
    @transaction.atomic
    def update_final_professor_assignments(
        final_exam, selected_professor_ids: list[str]
    ) -> dict:
        return AssignmentService._update_assignments(
            final_exam, selected_professor_ids, "final"
        )
