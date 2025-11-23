from .base import BaseRepository
from app.models.student import Student


class StudentRepository(BaseRepository):
    """Repository for Student model access."""

    def __init__(self):
        super().__init__(Student)

    def by_user_id_with_career_faculty(self, user_id):
        """Retrieve a student by user ID with career and faculty selected.

        Args:
            user_id: The user ID.

        Returns:
            The Student instance or None.
        """
        qs = self.list(filters={"user_id": user_id}, select_related=("career__faculty",))
        return qs.first()

    def list_by_career(self, career_code):
        """List students by career code with user selected.

        Args:
            career_code: The career code.

        Returns:
            Queryset of Student instances.
        """
        return self.list(filters={"career__code": career_code}, select_related=("user",))
