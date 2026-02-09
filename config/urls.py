from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from config.health_check import health_check

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("django-admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("", include("users.urls")),
    path("", include("academics.urls")),
    path("", include("enrollments.urls")),
    path("", include("grading.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
