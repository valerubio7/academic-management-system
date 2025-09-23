from .base import BaseRepository
from app.models.career import Career


class CareerRepository(BaseRepository):
    """Repository for Career model access."""

    def __init__(self):
        super().__init__(Career)

    def list_all(self):
        """List all careers ordered by name with faculty selected."""
        return self.list(order_by=("name",), select_related=("faculty",))

    def by_code(self, code):
        """Retrieve a career by its code with faculty selected.

        Args:
            code: The career code.

        Returns:
            The Career instance.
        """
        return self.get_one({"code": code}, select_related=("faculty",))

    def list_by_faculty(self, faculty_code):
        """List careers by faculty code ordered by name.

        Args:
            faculty_code: The faculty code.

        Returns:
            Queryset of Career instances.
        """
        return self.list(filters={"faculty__code": faculty_code}, order_by=("name",))
