from .base import BaseRepository
from app.models.custom_user import CustomUser


class UserRepository(BaseRepository):
    """Repository for CustomUser access."""

    def __init__(self):
        super().__init__(CustomUser)

    def list_all(self, *, order_by=None):
        return self.list(order_by=order_by)

    def list_by_role(self, role):
        return self.list(filters={"role": role})

    def by_username(self, username):
        return self.get_one({"username": username})

    def by_dni(self, dni):
        return self.get_one({"dni": dni})

    def with_profiles(self):
        return self.list(select_related=("student", "professor", "administrator"))
