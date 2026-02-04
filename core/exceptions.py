"""
Core exceptions for the academic management system.
"""


class ServiceError(Exception):
    """
    Base exception for service layer errors.

    Attributes:
        service: Name of the service where the error occurred
        operation: Operation being performed
        message: Error message
        original_exception: Original exception that caused this error (if any)
    """

    def __init__(self, service, operation, message, original_exception=None):
        self.service = service
        self.operation = operation
        self.original_exception = original_exception
        super().__init__(f"{service}.{operation}: {message}")
