from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm


def user_login(request):
    """Authenticate and redirect to role-based dashboard."""
    def redirect_by_role(user):
        if user.role == 'student':
            return redirect('users:student-dashboard')
        if user.role == 'professor':
            return redirect('users:professor-dashboard')
        if user.role == 'administrator':
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
                next_url = request.GET.get('next')
                return redirect(next_url) if next_url else redirect_by_role(user)
            form.add_error(None, 'Incorrect username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {"form": form})


def user_logout(request):
    logout(request)
    return redirect('home')
