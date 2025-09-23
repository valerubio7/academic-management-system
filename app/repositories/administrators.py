from .base import BaseRepository
from app.models.administrator import Administrator


class AdministratorRepository(BaseRepository):
    """Repository for Administrator model access."""

    def __init__(self):
        super().__init__(Administrator)
