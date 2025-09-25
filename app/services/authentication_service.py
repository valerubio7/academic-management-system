"""
Simple authentication service for user login, logout, and role checking.
"""

from django.contrib.auth import authenticate, login, logout
from django.utils import timezone


class AuthenticationService:
    """
    Handles user login, logout, and permission checking.

    This service keeps authentication simple and easy to understand.
    """

    def __init__(self, user_repository):
        """Initialize with a user repository."""
        self.user_repository = user_repository

    def login_user(self, request, username, password):
        """
        Try to log in a user with username and password.

        Returns:
            dict: Contains success status, user info, and redirect URL
        """
        # Check if credentials are valid
        user = authenticate(request, username=username, password=password)

        if not user:
            return {'success': False, 'message': 'Invalid username or password'}

        if not user.is_active:
            return {'success': False, 'message': 'Account is inactive'}

        # Log the user in
        login(request, user)

        # Update last login time
        user.last_login = timezone.now()
        user.save()

        return {
            'success': True,
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'redirect_url': self._get_dashboard_url(user)
        }

    def logout_user(self, request):
        """Log out the current user."""
        logout(request)
        return {'success': True, 'message': 'Logged out successfully'}

    def is_user_allowed(self, user, required_role):
        """
        Check if user has the required role.

        Args:
            user: The user to check
            required_role: 'student', 'professor', or 'administrator'

        Returns:
            bool: True if user has permission
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers can access everything
        if user.is_superuser:
            return True

        # Check if user role matches required role
        return user.role == required_role

    def get_user_info(self, user):
        """Get basic user information."""
        if not user or not user.is_authenticated:
            return None

        return {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'full_name': user.get_full_name(),
            'is_active': user.is_active
        }

    def _get_dashboard_url(self, user):
        """Get the correct dashboard URL based on user role."""
        if user.role == 'student':
            return '/users/student-dashboard/'
        elif user.role == 'professor':
            return '/users/professor-dashboard/'
        elif user.role == 'administrator' or user.is_superuser:
            return '/users/admin-dashboard/'
        else:
            return '/'
