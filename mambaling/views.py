from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, AdminRegistrationForm, UserRegistrationForm
from .models import CustomUser

def landing_page(request):
    return render(request, 'landing_page.html')

def my_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    if user.is_approved:
                        login(request, user)
                        return redirect('dashboard')
                    else:
                        messages.error(request, "Your account is not yet approved.")
                else:
                    messages.error(request, "Your account is inactive.")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'my_login.html', {'form': form})

def register(request):
    return render(request, 'register.html')

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False
            user.save()
            messages.success(request, "Admin registration successful. Please wait for approval.")
            return redirect('my_login')
    else:
        form = AdminRegistrationForm()
    return render(request, 'registration_form.html', {'form': form, 'title': 'Admin Registration'})

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = False
            user.save()
            messages.success(request, "User registration successful. Please wait for approval.")
            return redirect('my_login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration_form.html', {'form': form, 'title': 'User Registration'})

@login_required
def dashboard(request):
    if not request.user.is_approved:
        messages.warning(request, "Your account is awaiting admin approval.")
        return redirect('landing_page')
    return render(request, 'dashboard/dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('my_login')

@user_passes_test(lambda u: u.is_superuser)
def approve_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = CustomUser.objects.get(id=user_id)
        if action == 'approve':
            user.is_approved = True
            user.save()
            messages.success(request, f"User {user.email} has been approved.")
        elif action == 'reject':
            user.delete()
            messages.success(request, f"User {user.email} has been rejected and deleted.")
    pending_users = CustomUser.objects.filter(is_approved=False)
    return render(request, 'approve_users.html', {'pending_users': pending_users})
