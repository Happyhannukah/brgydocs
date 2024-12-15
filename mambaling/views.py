from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import LoginForm, AdminRegistrationForm, UserRegistrationForm
from .models import CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

def landing_page(request):
    return render(request, 'landing_page.html')

# def my_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, email=email, password=password)
#             if user is not None:
#                 if user.is_active:
#                     if user.is_approved:
#                         login(request, user)
#                         if user.user_type == 'admin':
#                             return redirect('admin_dashboard')
#                         else:
#                             return redirect('user_dashboard')
#                     else:
#                         messages.error(request, "Your account is not yet approved.")
#                 else:
#                     messages.error(request, "Your account is inactive.")
#             else:
#                 messages.error(request, "Invalid email or password.")
#     else:
#         form = LoginForm()
#     return render(request, 'my_login.html', {'form': form})


def my_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)  # email as username
            if user is not None:
                if user.is_active:
                    if not user.is_approved:  # Optional approval logic
                        messages.error(request, "Your account is not yet approved.")
                    else:
                        login(request, user)
                        if user.user_type == 'admin':
                            return redirect('admin_dashboard')
                        else:
                            return redirect('user_dashboard')
                else:
                    messages.error(request, "Your account is inactive.")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'my_login.html', {'form': form})


def forgot_password(request):
    if request.method == 'POST':
        print(f"UID: {uid}, Token: {token}")
        email = request.POST.get('email')
        try:
            user = get_object_or_404(User, email=email)  # Ensure email exists
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID
            reset_link = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')  # Construct reset link

            # Send email
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link below to reset your password:\n{reset_link}',
                from_email='zeycaramales@gmail.com',  # Sender's email
                recipient_list=[email],  # Receiver's email
                fail_silently=False,
            )
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('login')
        except Exception as e:
            messages.error(request, "An error occurred or the email is not registered.")
    return render(request, 'forgot_password.html')


# def reset_password(request, uidb64, token):
#     print(f"UID: {uid}, Token: {token}")

#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#         token_generator = PasswordResetTokenGenerator()

#         if token_generator.check_token(user, token):
#             if request.method == 'POST':
#                 new_password = request.POST.get('password')
#                 user.password = make_password(new_password)  # Save new password
#                 user.save()
#                 messages.success(request, "Your password has been reset successfully.")
#                 return redirect('login')

#             return render(request, 'reset_password.html', {'valid_link': True})
#         else:
#             messages.error(request, "The reset link is invalid or has expired.")
#     except Exception as e:
#         messages.error(request, "An error occurred.")
#     return redirect('my_login')


def reset_password(request, uidb64, token):
    try:
        # Decode the UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        token_generator = PasswordResetTokenGenerator()

        # Check token validity
        if token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('password')
                user.set_password(new_password)  # Use set_password for hashing
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('login')

            return render(request, 'reset_password.html', {'valid_link': True})
        else:
            messages.error(request, "The reset link is invalid or has expired.")
    except User.DoesNotExist:
        messages.error(request, "Invalid user ID.")
    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, "An error occurred.")

    return redirect('forgot_password')





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
    if request.user.user_type == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('user_dashboard')

# @login_required
# def admin_dashboard(request):
#     if not request.user.is_approved or request.user.user_type != 'admin':
#         messages.warning(request, "You don't have permission to access the admin dashboard.")
#         return redirect('landing_page')
#     return render(request, 'dashboard/admin_dashboard.html')


# @login_required
# def admin_dashboard(request):
#     if not request.user.is_approved or request.user.user_type != 'admin':
#         messages.warning(request, "You don't have permission to access the admin dashboard.")
#         return redirect('landing_page')
    
#     user_list = User.objects.filter(is_active=True).order_by('-date_joined')  # Query users
#     paginator = Paginator(user_list, 10)  # Show 10 users per page
#     page_number = request.GET.get('page')
#     users = paginator.get_page(page_number)
    
#     context = {
#         'users': users
#     }
#     return render(request, 'dashboard/admin_dashboard.html', context)

def admin_dashboard(request):
    User = get_user_model()  # Get the custom user model
    user_list = User.objects.filter(is_active=True).order_by('-date_joined')  # Query active users
    # Rest of your code
    context = {'user_list': user_list}
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def user_dashboard(request):
    if not request.user.is_approved or request.user.user_type != 'user':
        messages.warning(request, "You don't have permission to access the user dashboard.")
        return redirect('landing_page')
    return render(request, 'dashboard/user_dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('my_login')

@user_passes_test(lambda u: u.is_superuser)
def approve_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            user = CustomUser.objects.get(id=user_id)
            if action == 'approve':
                user.is_approved = True
                user.save()
                messages.success(request, f"User {user.email} has been approved.")
            elif action == 'reject':
                user.delete()
                messages.success(request, f"User {user.email} has been rejected and deleted.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found.")
    pending_users = CustomUser.objects.filter(is_approved=False)
    return render(request, 'my_login/approve_users.html', {'pending_users': pending_users})

