from .base import BaseRepository
from app.models.subject import Subject


class SubjectRepository(BaseRepository):
    """Repository for Subject model access."""

    def __init__(self):
        super().__init__(Subject)

    def list_all_with_career(self):
        """List all subjects with career selected, ordered by career name and subject name."""
        return self.list(select_related=("career",), order_by=("career__name", "name"))

    def by_code_with_career(self, code):
        """Retrieve a subject by code with career selected.

        Args:
            code: The subject code.

        Returns:
            The Subject instance.
        """
        return self.get_one({"code": code}, select_related=("career",))

    def list_by_career(self, career_code):
        """List subjects by career code, ordered by year and name.

        Args:
            career_code: The career code.

        Returns:
            Queryset of Subject instances.
        """
        return self.list(filters={"career__code": career_code}, order_by=("year", "name"))
