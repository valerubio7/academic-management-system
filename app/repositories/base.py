class BaseRepository:

    def __init__(self, model):
        self.model = model

    # ---- Query helpers ----
    def get_queryset(self):
        return self.model.objects.all()

    def _apply_related(self, qs, *, select_related=None, prefetch_related=None):
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs

    # ---- CRUD ----
    def get_by_id(self, pk, *, select_related=None, prefetch_related=None):
        qs = self._apply_related(self.get_queryset(), select_related=select_related, prefetch_related=prefetch_related)
        return qs.get(pk=pk)

    def get_one(self, filters, *, select_related=None, prefetch_related=None, order_by=None):
        qs = self._apply_related(self.get_queryset(), select_related=select_related, prefetch_related=prefetch_related)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs.get(**filters)

    def list(self, *, filters=None, order_by=None, select_related=None, prefetch_related=None, limit=None, offset=None):
        qs = self._apply_related(self.get_queryset(), select_related=select_related, prefetch_related=prefetch_related)
        if filters:
            qs = qs.filter(**filters)
        if order_by:
            qs = qs.order_by(*order_by)
        if offset is not None:
            qs = qs[offset:]
        if limit is not None:
            qs = qs[:limit]
        return qs

    def exists(self, *, filters=None):
        qs = self.get_queryset()
        if filters:
            qs = qs.filter(**filters)
        return qs.exists()

    def create(self, data):
        return self.model.objects.create(**data)

    def update(self, instance, data):
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
