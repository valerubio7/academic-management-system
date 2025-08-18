"""Authentication forms for the Accounts app.

Provides a minimal login form with username and password fields.
"""

from django import forms
from django.contrib.auth import get_user_model


class LoginForm(forms.Form):
    """
    Username/password form used by the login view.

    Fields:
        username (forms.CharField): User identifier input.
        password (forms.CharField): Password input rendered with a password widget.

    Notes:
        Labels are in Spanish to match the current UI.
    """
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
