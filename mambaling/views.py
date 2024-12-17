from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from mambaling.utils import fill_clearance_template
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
from .forms import LoginForm, AdminRegistrationForm, UserRegistrationForm, ProfileEditForm
from .models import ClearanceRequest
from django.views.decorators.http import require_POST
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
import io
from datetime import datetime
from django.http import FileResponse
import os
from django.http import FileResponse
from django.conf import settings
from datetime import datetime
from docx import Document
template_path = os.path.join(settings.BASE_DIR, 'templates/2024-barangay-clearance-final.docx')
output_path = os.path.join(settings.BASE_DIR, 'media/preview_clearance.docx')


def landing_page(request):
    return render(request, 'landing_page.html')

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

def reset_password(request, uidb64, token):
    try:
        # Decode the UID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))  # Ensure the UID is properly decoded
        user = User.objects.get(pk=uid)  # Fetch the user object

        # Generate the token
        token_generator = PasswordResetTokenGenerator()

        # Check if the token is valid
        if token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('password')
                user.set_password(new_password)  # Hash the new password
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('login')  # Redirect to the login page after reset

            # Render the reset password page with a valid link
            return render(request, 'reset_password.html', {'valid_link': True})

        else:
            # Invalid or expired token
            messages.error(request, "The reset link is invalid or has expired.")
    except User.DoesNotExist:
        # Handle case where the user is not found
        messages.error(request, "Invalid user ID.")
    except Exception as e:
        # Log any other exceptions
        print(f"Error: {e}")
        messages.error(request, "An error occurred.")

    # If any issue occurs, redirect to the forgot password page
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


@login_required
def admin_dashboard(request):
    # Ensure only admin can access
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('landing_page')

    # Fetch clearance requests and apply pagination
    clearance_requests = ClearanceRequest.objects.order_by('-date_requested')
    paginator = Paginator(clearance_requests, 10)  # Show 10 requests per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count statuses
    approved_count = ClearanceRequest.objects.filter(status="Approved").count()
    declined_count = ClearanceRequest.objects.filter(status="Declined").count()
    pending_count = ClearanceRequest.objects.filter(status="Pending").count()

    context = {
        'requests': page_obj,  # Paginated data
        'approved_count': approved_count,
        'declined_count': declined_count,
        'pending_count': pending_count,
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def user_dashboard(request):
    if not request.user.is_approved or request.user.user_type != 'user':
        messages.warning(request, "You don't have permission to access the user dashboard.")
        return redirect('landing_page')
    return render(request, 'dashboard/user_dashboard.html')

def user_logout(request):
    logout(request)
    return redirect('landing_page')

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


@login_required
def profile_admin(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)  # Add request.FILES
        if form.is_valid():
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            form.save()
            messages.success(request, 'Profile updated successfully!')  # Add success message
            return redirect('profile_admin')  # Redirect to the same page
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'dashboard/admin/profile_admin.html', {'user': user, 'form': form})


@login_required
def barangay_clearance(request):
    # Define the correct path to the .docx template
    template_path = os.path.join(settings.BASE_DIR, 'mambaling', 'templates', '2024-barangay-clearance-final.docx')
    output_path = os.path.join(settings.MEDIA_ROOT, 'preview_clearance.docx')

    # Debugging: Print resolved paths to verify correctness
    print(f"Template path: {template_path}")
    print(f"Output path: {output_path}")

    # Check if the template file exists
    if not os.path.exists(template_path):
        messages.error(request, "The Barangay Clearance template file is missing.")
        return redirect('user_dashboard')  # Redirect the user if the template file is missing

    # Handle form submission
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        purpose = request.POST.get("purpose")

        if not name or not address or not purpose:
            messages.error(request, "All fields are required.")
            return render(request, 'barangay_clearance_form.html', {
                'name': name,
                'address': address,
                'purpose': purpose,
            })

        # Prepare data for template
        data = {
            '{{name}}': name,
            '{{address}}': address,
            '{{purpose}}': purpose,
            '{{date}}': datetime.now().strftime('%B %d, %Y'),
        }

        # Fill the template and save the output
        try:
            fill_clearance_template(template_path, output_path, data)
        except Exception as e:
            print(f"Error processing template: {e}")
            messages.error(request, "An error occurred while generating your document.")
            return redirect('user_dashboard')

        # Preview logic
        if 'preview' in request.POST:
            return FileResponse(open(output_path, 'rb'), as_attachment=False,
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

        # Save request to the database
        ClearanceRequest.objects.create(
            user=request.user,
            full_name=name,
            address=address,
            type=purpose,
            status='Pending'
        )
        messages.success(request, "Barangay Clearance request submitted successfully.")
        return redirect('user_dashboard')

    return render(request, 'barangay_clearance_form.html')

@require_POST
@login_required
def update_request_status(request, request_id):
    clearance_request = get_object_or_404(ClearanceRequest, id=request_id)

    new_status = request.POST.get("status")
    if new_status in ['Pending', 'Approved', 'Declined']:
        clearance_request.status = new_status
        clearance_request.save()
        messages.success(request, "Request status updated successfully.")
    else:
        messages.error(request, "Invalid status update.")

    return redirect('admin_dashboard')

def generate_clearance_pdf(data):
    """
    Generate Barangay Clearance PDF with pre-filled user data.
    :param data: Dictionary containing name, address, and purpose.
    :return: PDF response
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Barangay Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 750, "Republic of the Philippines")
    c.drawString(200, 735, "City of Cebu")
    c.drawString(200, 720, "BARANGAY MAMBALING")
    c.drawString(200, 705, "OFFICE OF THE BARANGAY CAPTAIN")

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(230, 680, "BARANGAY CLEARANCE")

    # Body Content
    c.setFont("Helvetica", 12)
    c.drawString(50, 640, f"This is to certify that {data['name']}, residing at")
    c.drawString(50, 620, f"{data['address']}, Barangay Mambaling, Cebu City, has requested")
    c.drawString(50, 600, f"this certificate for the purpose of {data['purpose']}.")

    c.drawString(50, 560, f"Given this {data['date']} at Barangay Hall, Mambaling, Cebu City, Philippines.")
    c.drawString(50, 520, "NOT VALID WITHOUT OFFICIAL SEAL.")

    # Signature
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, 480, "HON. ROSELLER V. SALVADOR")
    c.drawString(400, 460, "Barangay Captain")

    # Save and return PDF
    c.save()
    buffer.seek(0)
    return buffer

@login_required
def download_clearance_pdf(request, request_id):
    # Ensure only admin can download
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to download this document.")
        return redirect('landing_page')

    # Get the approved request
    clearance_request = get_object_or_404(ClearanceRequest, id=request_id, status='Approved')

    # Paths
    template_path = os.path.join(settings.BASE_DIR, 'templates/2024-barangay-clearance-final.docx')
    output_path = os.path.join(settings.MEDIA_ROOT, f'final_clearance_{clearance_request.id}.docx')

    # Fill the template with request data
    data = {
        '{{name}}': clearance_request.full_name,
        '{{address}}': clearance_request.address,
        '{{purpose}}': clearance_request.type,
        '{{date}}': clearance_request.date_requested.strftime('%B %d, %Y'),
    }
    fill_clearance_template(template_path, output_path, data)

    # Serve the document as a file response
    return FileResponse(open(output_path, 'rb'), as_attachment=True,
                        filename=f"Barangay_Clearance_{clearance_request.full_name}.docx")





