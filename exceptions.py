class ServiceError(Exception):
    """Base exception for service layer errors."""

    def __init__(
        self,
        *args,
        service=None,
        operation=None,
        message=None,
        original_exception=None,
        **kwargs,
    ):
        """
        Initialize ServiceError with flexible arguments.

        Can be used in multiple ways:
        - ServiceError(service, operation, message)
        - ServiceError(service=name, operation=op, message=msg, original_exception=e)
        - ServiceError(message)
        """
        if message:
            super().__init__(message)
            self.message = message
        elif args:
            super().__init__(*args)
            self.message = str(args[0]) if args else ""
        else:
            super().__init__()
            self.message = ""

        self.service = service
        self.operation = operation
        self.original_exception = original_exception
