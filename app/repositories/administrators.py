from .base import BaseRepository
from app.models.administrator import Administrator


class AdministratorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Administrator)
