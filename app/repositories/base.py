class BaseRepository:
    """Base repository class providing common CRUD operations and query helpers for Django models."""

    def __init__(self, model):
        """Initialize the repository with a Django model.

        Args:
            model: The Django model class this repository manages.
        """
        self.model = model

    # ---- Query helpers ----
    def get_queryset(self):
        """Return the base queryset for the model."""
        return self.model.objects.all()

    def _apply_related(self, qs, *, select_related=None, prefetch_related=None):
        """Apply select_related and prefetch_related to a queryset.

        Args:
            qs: The queryset to modify.
            select_related: List of related fields to select.
            prefetch_related: List of related fields to prefetch.

        Returns:
            Modified queryset.
        """
        if select_related:
            qs = qs.select_related(*select_related)
        if prefetch_related:
            qs = qs.prefetch_related(*prefetch_related)
        return qs

    # ---- CRUD ----
    def get_by_id(self, pk, *, select_related=None, prefetch_related=None):
        """Retrieve a single instance by primary key.

        Args:
            pk: Primary key of the instance.
            select_related: List of related fields to select.
            prefetch_related: List of related fields to prefetch.

        Returns:
            The model instance.
        """
        qs = self._apply_related(self.get_queryset(), select_related=select_related, prefetch_related=prefetch_related)
        return qs.get(pk=pk)

    def get_one(self, filters, *, select_related=None, prefetch_related=None, order_by=None):
        """Retrieve a single instance matching the filters.

        Args:
            filters: Dictionary of field filters.
            select_related: List of related fields to select.
            prefetch_related: List of related fields to prefetch.
            order_by: List of fields to order by.

        Returns:
            The model instance.
        """
        qs = self._apply_related(self.get_queryset(), select_related=select_related, prefetch_related=prefetch_related)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs.get(**filters)

    def list(self, *, filters=None, order_by=None, select_related=None, prefetch_related=None, limit=None, offset=None):
        """Retrieve a list of instances with optional filters and ordering.

        Args:
            filters: Dictionary of field filters.
            order_by: List of fields to order by.
            select_related: List of related fields to select.
            prefetch_related: List of related fields to prefetch.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            Queryset of model instances.
        """
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
        """Check if any instances match the filters.

        Args:
            filters: Dictionary of field filters.

        Returns:
            True if any instances exist, False otherwise.
        """
        qs = self.get_queryset()
        if filters:
            qs = qs.filter(**filters)
        return qs.exists()

    def create(self, data):
        """Create a new instance with the given data.

        Args:
            data: Dictionary of field values.

        Returns:
            The created model instance.
        """
        return self.model.objects.create(**data)

    def update(self, instance, data):
        """Update an existing instance with the given data.

        Args:
            instance: The model instance to update.
            data: Dictionary of field values to update.

        Returns:
            The updated model instance.
        """
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, instance):
        """Delete the given instance.

        Args:
            instance: The model instance to delete.
        """
        instance.delete()
