from .base import BaseRepository
from app.models.final_exam import FinalExam


class FinalExamRepository(BaseRepository):
    def __init__(self):
        super().__init__(FinalExam)

    def list_all_with_subject(self):
        return self.list(select_related=("subject",), order_by=("-date",))

    def by_id_with_subject(self, pk):
        return self.get_by_id(pk, select_related=("subject",))

    def list_by_subject_ids(self, subject_ids):
        return self.list(filters={"subject_id__in": subject_ids}, order_by=("date",))
