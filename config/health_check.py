"""
Health check endpoint for monitoring and load balancers.

This module provides a simple health check view that verifies:
- Django application is running
- Database connection is working
- Basic system health

Usage:
    Add to urls.py:
    from config.health_check import health_check
    path('health/', health_check, name='health_check'),
"""

from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Health check endpoint for monitoring.

    Returns:
        JsonResponse: JSON response with health status
            - 200 OK if healthy (database connection works)
            - 503 Service Unavailable if unhealthy

    Response format:
        {
            "status": "healthy" | "unhealthy",
            "database": "connected" | "error",
            "error": "error message" (only if unhealthy)
        }
    """
    health_status = {"status": "healthy", "database": "connected"}

    try:
        # Test database connection
        connection.ensure_connection()

        # Simple query to verify database is responsive
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse(health_status, status=200)

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "error"
        health_status["error"] = str(e)

        return JsonResponse(health_status, status=503)
