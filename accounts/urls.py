"""URL patterns for the Accounts app.

Routes:
- /login/  -> views.user_login   (name="login")
- /logout/ -> views.user_logout  (name="logout")

Notes:
    Namespaced via app_name to allow reverse('accounts:login').
"""

from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
