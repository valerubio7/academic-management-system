from .base import BaseRepository
from app.models.faculty import Faculty


class FacultyRepository(BaseRepository):
    """Repository for Faculty model access."""

    def __init__(self):
        super().__init__(Faculty)

    def list_all(self):
        """List all faculties ordered by name."""
        return self.list(order_by=("name",))

    def by_code(self, code):
        """Retrieve a faculty by its code.

        Args:
            code: The faculty code.

        Returns:
            The Faculty instance.
        """
        return self.get_one({"code": code})
