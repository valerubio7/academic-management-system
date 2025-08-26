"""Views for the Accounts app.

Includes:
- user_login: authenticates users and redirects by role or `next` param.
- user_logout: logs out the current user and redirects to home.
"""

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm


def user_login(request):
    """
    Authenticate a user and redirect to the appropriate dashboard.

    Behavior:
        - If already authenticated, redirect based on the user's role.
        - On POST, validate credentials via LoginForm and authenticate.
        - If successful, log in and redirect to `next` (if provided) or to a role-based dashboard.
        - On failure, attach a non-field error to the form and re-render the template.

    Args:
        request (HttpRequest): Incoming request.

    Returns:
        HttpResponse: Redirect to dashboard/home or rendered login page.

        Notes:
                - Assumes the user model exposes a `role` attribute with values
                    {'student', 'professor', 'administrator'}.
                - Superusers are treated as administrators for redirects, and on login
                    their persisted `role` is normalized to 'administrator' if needed.
                - The UI labels in LoginForm are in Spanish to match the current UI.
    """
    # Helper to centralize role-based redirects.
    def redirect_by_role(user):
        # If the logged user is a Django superuser, ensure they have the
        # administrator role persisted (in case it wasn't set yet).
        if getattr(user, 'is_superuser', False) and getattr(user, 'role', None) != 'administrator':
            user.role = 'administrator'
            user.save(update_fields=['role'])

        if getattr(user, 'role', None) == 'student':
            return redirect('users:student-dashboard')
        if getattr(user, 'role', None) == 'professor':
            return redirect('users:professor-dashboard')
        # Treat superusers as administrators regardless of the role field
        if getattr(user, 'role', None) == 'administrator' or getattr(user, 'is_superuser', False):
            return redirect('users:admin-dashboard')
        return redirect('home')

    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        if (form := LoginForm(request.POST)).is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if user := authenticate(request, username=username, password=password):
                login(request, user)

                # If this account is a superuser, ensure the persistent role is set
                if getattr(user, 'is_superuser', False) and getattr(user, 'role', None) != 'administrator':
                    user.role = 'administrator'
                    user.save(update_fields=['role'])

                next_url = request.GET.get('next')
                return redirect(next_url) if next_url else redirect_by_role(user)
            form.add_error(None, 'Incorrect username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {"form": form})


def user_logout(request):
    """
    Log out the current user and redirect to the home page.

    Args:
        request (HttpRequest): Incoming request.

    Returns:
        HttpResponseRedirect: Redirect to 'home'.
    """
    logout(request)
    return redirect('home')
