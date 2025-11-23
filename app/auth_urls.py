"""URL patterns for authentication.

Routes:
- /login/  -> views.user_login   (name="login")
- /logout/ -> views.user_logout  (name="logout")
"""

from django.urls import path

from app.views import auth_views

urlpatterns = [
    path('login/', auth_views.user_login, name='login'),
    path('logout/', auth_views.user_logout, name='logout'),
]