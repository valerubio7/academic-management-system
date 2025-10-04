"""
Service for user management operations.

Business logic for user and profile management.
Coordinates between repositories to maintain data consistency.
"""

from django.db import transaction
from django.contrib.auth.hashers import make_password
from typing import Dict, Any, Optional

from app.repositories import UserRepository, StudentRepository, ProfessorRepository, AdministratorRepository


class UserManagementServiceError(Exception):
    """Base exception for user management operations."""
    pass


class UserManagementService:
    """
    Manages users and their role-specific profiles.

    Business rules:
    - Every user must have exactly one role-specific profile
    - User data and profile data are created/updated atomically
    - Profile data is validated according to role requirements
    """

    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        student_repository: Optional[StudentRepository] = None,
        professor_repository: Optional[ProfessorRepository] = None,
        administrator_repository: Optional[AdministratorRepository] = None
    ):
        # Repositories: data access only
        self.user_repository = user_repository or UserRepository()
        self.student_repository = student_repository or StudentRepository()
        self.professor_repository = professor_repository or ProfessorRepository()
        self.administrator_repository = administrator_repository or AdministratorRepository()

    def create_user_with_profile(self, user_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Any:
        """
        Create user and role-specific profile atomically.

        Business rules:
        - Profile data is mandatory
        - Password is automatically hashed
        - User and profile created in single transaction
        """
        if not profile_data or 'role' not in user_data:
            raise UserManagementServiceError("Profile data and role are required")

        try:
            with transaction.atomic():
                # Hash password
                if 'password' in user_data:
                    user_data['password'] = make_password(user_data['password'])

                # Create user via repository
                user = self.user_repository.create(user_data)

                # Create profile via appropriate repository
                self._create_profile_for_user(user, profile_data)

                return user

        except Exception as e:
            raise UserManagementServiceError(f"Failed to create user: {str(e)}") from e

    def update_user_profile(self, user: Any, user_data: Dict[str, Any]) -> Any:
        """
        Update user data (role changes not supported).

        Business rules:
        - Empty passwords are ignored (not updated)
        - User data updated via repository
        """
        try:
            with transaction.atomic():
                # Hash password if provided and not empty
                if 'password' in user_data and user_data['password']:
                    user_data['password'] = make_password(user_data['password'])
                elif 'password' in user_data:
                    del user_data['password']  # Remove empty password

                # Update via repository
                return self.user_repository.update(user, user_data)

        except Exception as e:
            raise UserManagementServiceError(f"Failed to update user: {str(e)}") from e

    def delete_user(self, user: Any) -> bool:
        """
        Delete user (profiles are cascade deleted by Django).
        """
        try:
            with transaction.atomic():
                self.user_repository.delete(user)
                return True
        except Exception as e:
            raise UserManagementServiceError(f"Failed to delete user: {str(e)}") from e

    def get_user_with_profile(self, user_id: int):
        """Get user with profile loaded via repository."""
        return self.user_repository.get_by_id(user_id, select_related=['student', 'professor', 'administrator'])

    def list_all_users_with_profiles(self):
        """List all users with profiles via repository."""
        return self.user_repository.with_profiles()

    def create_user_profile(self, user: Any) -> None:
        """
        Create role-specific profile for an existing user.
        
        Business rules:
        - User must have a role assigned
        - Creates profile with default values based on user role
        """
        from datetime import date
        
        try:
            with transaction.atomic():
                profile_data = {}
                
                # Set default values based on role
                if user.role == user.Role.STUDENT:
                    profile_data = {
                        'student_id': f'STU{user.id:05d}',
                        'enrollment_date': date.today(),
                        'career': None  # Career is optional and can be set later
                    }
                elif user.role == user.Role.PROFESSOR:
                    profile_data = {
                        'professor_id': f'PROF{user.id:05d}',
                        'degree': 'Sin especificar',
                        'category': 'auxiliar',  # Default to auxiliar category
                        'hire_date': date.today()
                    }
                elif user.role == user.Role.ADMIN:
                    profile_data = {
                        'administrator_id': f'ADM{user.id:05d}',
                        'position': 'Administrador',
                        'hire_date': date.today()
                    }
                
                self._create_profile_for_user(user, profile_data)
        except Exception as e:
            raise UserManagementServiceError(f"Failed to create user profile: {str(e)}") from e

    def _create_profile_for_user(self, user: Any, profile_data: Dict[str, Any]) -> None:
        """Create role-specific profile via appropriate repository."""
        profile_data_with_user = {**profile_data, 'user': user}

        # Import to use proper enum values
        from app.models.custom_user import CustomUser
        
        if user.role == CustomUser.Role.STUDENT:
            self.student_repository.create(profile_data_with_user)
        elif user.role == CustomUser.Role.PROFESSOR:
            self.professor_repository.create(profile_data_with_user)
        elif user.role == CustomUser.Role.ADMIN:
            self.administrator_repository.create(profile_data_with_user)
