import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """Health check endpoint for Railway/monitoring.

    Returns 200 if the application process is running and able to serve requests.
    Does NOT check the database — Railway's healthcheck only needs to confirm
    the web server is alive. Database issues are handled by Django at request time.
    """
    return JsonResponse({"status": "ok"}, status=200)
