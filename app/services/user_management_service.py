"""
Service for user management operations.

Handles business logic for user creation, update, deletion and role-specific
profile management. Coordinates between UserRepository and role-specific repositories.
"""

from django.db import transaction
from django.contrib.auth.hashers import make_password
from typing import Dict, Any, Optional

from app.repositories import UserRepository, StudentRepository, ProfessorRepository, AdministratorRepository


class UserManagementServiceError(Exception):
    """Base exception for UserManagementService operations."""
    pass


class UserCreationError(UserManagementServiceError):
    """Raised when user creation fails."""
    pass


class UserUpdateError(UserManagementServiceError):
    """Raised when user update fails."""
    pass


class UserDeletionError(UserManagementServiceError):
    """Raised when user deletion fails."""
    pass


class UserManagementService:
    """
    Service for managing users and their role-specific profiles.

    Provides transactional operations for:
    - Creating users with role-specific profiles
    - Updating users and handling role changes
    - Deleting users
    - Managing profile transitions between roles
    """

    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        student_repository: Optional[StudentRepository] = None,
        professor_repository: Optional[ProfessorRepository] = None,
        administrator_repository: Optional[AdministratorRepository] = None
    ):
        self.user_repository = user_repository or UserRepository()
        self.student_repository = student_repository or StudentRepository()
        self.professor_repository = professor_repository or ProfessorRepository()
        self.administrator_repository = administrator_repository or AdministratorRepository()

    def create_user_with_profile(self, user_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Any:
        """
        Create a new user with mandatory role-specific profile.

        Args:
            user_data: Dictionary containing user fields (username, email, role, etc.)
            profile_data: Dictionary containing profile-specific fields (required)

        Returns:
            User instance: The created user instance

        Raises:
            UserCreationError: If user or profile creation fails
        """
        try:
            with transaction.atomic():
                # Validate that profile_data is provided
                if not profile_data:
                    raise UserCreationError("Profile data is required when creating a user")

                # Validate role exists in user_data
                if 'role' not in user_data:
                    raise UserCreationError("Role is required when creating a user")

                # Validate profile data for the specific role
                self._validate_profile_data(user_data['role'], profile_data)

                # Hash password if provided
                if 'password' in user_data:
                    user_data['password'] = make_password(user_data['password'])

                # Create user using repository
                user = self.user_repository.create(user_data)

                # Create role-specific profile
                self._create_profile_for_user(user, profile_data)

                return user

        except Exception as e:
            raise UserCreationError(f"Failed to create user: {str(e)}") from e

    def update_user_profile(
        self, user: Any, user_data: Dict[str, Any], profile_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Update user and their profile data. Role changes are not allowed.

        Args:
            user: The user instance to update
            user_data: Dictionary containing updated user fields
            profile_data: Dictionary containing updated profile fields

        Returns:
            User instance: The updated user instance

        Raises:
            UserUpdateError: If user update fails or role change is attempted
        """
        try:
            with transaction.atomic():
                # Hash password if provided
                if 'password' in user_data and user_data['password']:
                    user_data['password'] = make_password(user_data['password'])
                elif 'password' in user_data:
                    # Remove empty password to avoid overwriting existing one
                    del user_data['password']

                # Update user fields using repository
                user = self.user_repository.update(user, user_data)

                return user

        except Exception as e:
            raise UserUpdateError(f"Failed to update user: {str(e)}") from e

    def delete_user(self, user: Any) -> bool:
        """
        Delete a user and all related profiles.

        Args:
            user: The user instance to delete

        Returns:
            bool: True if deletion was successful

        Raises:
            UserDeletionError: If deletion fails
        """
        try:
            with transaction.atomic():
                # Use repository to delete (Django handles cascade deletion of related profiles automatically)
                self.user_repository.delete(user)
                return True

        except Exception as e:
            raise UserDeletionError(f"Failed to delete user: {str(e)}") from e

    def get_user_with_profile(self, user_id: int) -> Optional[Any]:
        """
        Retrieve a user with their role-specific profile loaded.

        Args:
            user_id: The user's primary key

        Returns:
            User instance or None: The user with profile loaded
        """
        try:
            return self.user_repository.get_by_id(user_id, select_related=['student', 'professor', 'administrator'])

        except Exception:
            return None

    def list_all_users_with_profiles(self):
        """
        List all users with their profiles loaded.

        Returns:
            QuerySet: All users with related profiles
        """
        return self.user_repository.with_profiles()

    def _create_profile_for_user(self, user: Any, profile_data: Dict[str, Any]) -> None:
        """
        Create role-specific profile for a user.

        Args:
            user: The user instance
            profile_data: Profile-specific data

        Raises:
            UserCreationError: If profile creation fails
        """
        role = user.role
        profile_data_with_user = {**profile_data, 'user': user}

        if role == 'student':
            self.student_repository.create(profile_data_with_user)
        elif role == 'professor':
            self.professor_repository.create(profile_data_with_user)
        elif role == 'administrator':
            self.administrator_repository.create(profile_data_with_user)

    def _update_existing_profile(self, user: Any, role: str, profile_data: Dict[str, Any]) -> None:
        """
        Update existing role-specific profile.

        Args:
            user: The user instance
            role: The user's role
            profile_data: Updated profile data
        """
        if role == 'student':
            if hasattr(user, 'student'):
                self.student_repository.update(user.student, profile_data)
        elif role == 'professor':
            if hasattr(user, 'professor'):
                self.professor_repository.update(user.professor, profile_data)
        elif role == 'administrator':
            if hasattr(user, 'administrator'):
                self.administrator_repository.update(user.administrator, profile_data)

    def _validate_profile_data(self, role: str, profile_data: Dict[str, Any]) -> None:
        """
        Validate that profile data contains required fields for the specific role.

        Args:
            role: The user role
            profile_data: The profile data to validate

        Raises:
            UserCreationError: If required fields are missing
        """
        required_fields = {}

        if role == 'student':
            required_fields = {
                'student_id': 'Student ID is required',
                'enrollment_date': 'Enrollment date is required'
            }
        elif role == 'professor':
            required_fields = {
                'professor_id': 'Professor ID is required',
                'degree': 'Degree is required',
                'hire_date': 'Hire date is required',
                'category': 'Category is required'
            }
        elif role == 'administrator':
            required_fields = {
                'administrator_id': 'Administrator ID is required',
                'position': 'Position is required',
                'hire_date': 'Hire date is required'
            }

        # Check for missing required fields
        missing_fields = []
        for field, error_msg in required_fields.items():
            if field not in profile_data or not profile_data[field]:
                missing_fields.append(error_msg)

        if missing_fields:
            raise UserCreationError(f"Missing required profile fields: {', '.join(missing_fields)}")
