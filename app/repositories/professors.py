from .base import BaseRepository
from app.models.professor import Professor


class ProfessorRepository(BaseRepository):
    """Repository for Professor model access."""

    def __init__(self):
        super().__init__(Professor)

    def list_all_with_user(self):
        """List all professors with user selected, ordered by user name."""
        return self.list(select_related=("user",), order_by=("user__last_name", "user__first_name"))
