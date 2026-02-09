import logging

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """Health check endpoint for monitoring. Returns 200 if healthy, 503 if unhealthy."""
    health_status = {"status": "healthy", "database": "connected"}

    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse(health_status, status=200)

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        health_status.update(
            {"status": "unhealthy", "database": "error", "error": str(e)}
        )
        return JsonResponse(health_status, status=503)
