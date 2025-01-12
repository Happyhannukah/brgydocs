from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from mambaling.utils import fill_clearance_template
from .forms import LoginForm, AdminRegistrationForm, UserRegistrationForm
from .models import CustomUser, ProofOfResidency
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import get_object_or_404
from .utils import generate_document
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
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import FileResponse
import os
from .models import ClearanceRequest, Notification
from django.http import FileResponse
from django.conf import settings
from datetime import datetime
from docx import Document
from django.views.decorators.http import require_POST
from .models import ClearanceRequest, Notification
from django.core.files.storage import default_storage
template_path = os.path.join(settings.BASE_DIR, 'templates/2024-barangay-clearance-final.docx')
output_path = os.path.join(settings.BASE_DIR, 'media/preview_clearance.docx')
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from docx import Document
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os
from django.db.models import Q 
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

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


# def forgot_password(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')

#         try:
#             user = CustomUser.objects.get(email=email)
#             token_generator = PasswordResetTokenGenerator()
#             token = token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             reset_link = request.build_absolute_uri(f'/reset-password/{uid}/{token}/')

#             # Generate email content
#             html_message = render_to_string('email_templates/password_reset_email.html', {'reset_link': reset_link})
#             plain_message = strip_tags(html_message)

#             # Send email
#             send_mail(
#                 subject='Password Reset Request',
#                 message=plain_message,
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[email],
#                 fail_silently=False,
#                 html_message=html_message,  # Include the HTML message
#             )
#             messages.success(request, 'A password reset link has been sent to your email.')
#             return redirect('my_login')

#         except CustomUser.DoesNotExist:
#             messages.error(request, "The email address is not registered.")
#             return render(request, 'forgot_password.html')

#     return render(request, 'forgot_password.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()  # Dynamically get the custom user model
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={
                    'uidb64': uid,
                    'token': token
                })
            )
            # Send email
            subject = 'Password Reset Request'
            message = f'Click the link below to reset your password:\n\n{reset_link}'
            from_email = 'zeycaramales@gmail.com'  # Replace with your email
            recipient_list = [email]

            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False
            )
            messages.success(request, 'Password reset email has been sent.')
            return redirect('my_login')  # Redirect to the same page or login page
        except User.DoesNotExist:
            messages.error(request, 'Email not found.')
            return redirect('forgot_password')
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
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to access the admin dashboard.")
        return redirect('landing_page')

    clearance_requests = ClearanceRequest.objects.order_by('-date_requested')
    
    approved_count = clearance_requests.filter(status="Approved").count()
    declined_count = clearance_requests.filter(status="Declined").count()
    pending_count = clearance_requests.filter(status="Pending").count()

    context = {
        'requests': clearance_requests,
        'approved_count': approved_count,
        'declined_count': declined_count,
        'pending_count': pending_count,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def get_request_details(request, request_id):
    clearance_request = get_object_or_404(ClearanceRequest, id=request_id)
    return render(request, 'dashboard/request_details_modal.html', {'request': clearance_request})

@login_required
def certificate_requests(request):
    # Check if the user has permission to access the page
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('landing_page')

    # Fetch certificate requests (filter by type if needed)
    certificate_requests = ClearanceRequest.objects.filter(type='Others').order_by('-date_requested')

    # Count statuses
    approved_count = certificate_requests.filter(status="Approved").count()
    declined_count = certificate_requests.filter(status="Declined").count()
    pending_count = certificate_requests.filter(status="Pending").count()

    # Pass the data to the context for rendering
    context = {
        'requests': certificate_requests,  # All certificate requests (no pagination)
        'approved_count': approved_count,
        'declined_count': declined_count,
        'pending_count': pending_count,
    }

    # Render the template
    return render(request, 'dashboard/admin/certificate_requests.html', context)


@login_required
def admin_profile(request):
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('landing_page')

    if request.method == 'POST':
        # Handle profile update
        profile_picture = request.FILES.get('profile_picture')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if profile_picture:
            request.user.profile_picture = profile_picture
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        messages.success(request, "Profile updated successfully.")

        # Handle password change
        if 'old_password' in request.POST:
            old_password = request.POST['old_password']
            new_password = request.POST['new_password']
            confirm_new_password = request.POST['confirm_new_password']

            if new_password == confirm_new_password:
                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    update_session_auth_hash(request, request.user)  # Prevent logout
                    messages.success(request, "Password changed successfully.")
                else:
                    messages.error(request, "Old password is incorrect.")
            else:
                messages.error(request, "New passwords do not match.")

    context = {
        'admin': request.user,
    }
    return render(request, 'dashboard/admin/admin_profile.html', context)

from django.core.mail import send_mail

def send_approval_email(request):
    subject = 'Your Barangay Clearance Request has been Approved'
    message = 'Your requested document is approved and ready for claiming at the barangay office.'
    from_email = 'noreply@barangay.com'
    recipient_list = [request.user.email]
    send_mail(subject, message, from_email, recipient_list)


@login_required
def generate_final_document(request, request_id):
    # Fetch the clearance request
    clearance_request = get_object_or_404(ClearanceRequest, id=request_id, status='Approved')

    # Map document type to correct template
    template_mapping = {
        'Barangay Clearance': os.path.join(settings.BASE_DIR, 'mambaling', 'templates', '2024-barangay-clearance-final.docx'),
        'Certificate of Residency': os.path.join(settings.BASE_DIR, 'mambaling', 'templates', '2024-CERT.-OF-RESIDENCY1.docx'),
        'Certificate of Indigency': os.path.join(settings.BASE_DIR, 'mambaling', 'templates', 'barangay-indigency-written.docx'),
    }

    template_file = template_mapping.get(clearance_request.document_type)
    if not template_file:
        messages.error(request, "Invalid document type.")
        return redirect('admin_dashboard')

    # Debugging: print the template path
    print(f"Template Path: {template_file}")

    try:
        # Load the document
        document = Document(template_file)

        # Replace placeholders with user information
        placeholders = {
            '{{name}}': clearance_request.full_name,
            '{{address}}': clearance_request.address,
            '{{purpose}}': clearance_request.purpose,
            '{{date}}': datetime.now().strftime('%B %d, %Y'),
        }
        for paragraph in document.paragraphs:
            for key, value in placeholders.items():
                if key in paragraph.text:
                    paragraph.text = paragraph.text.replace(key, value)

        # Save the modified document
        output_path = os.path.join(settings.MEDIA_ROOT, f'final_clearance_{clearance_request.id}.docx')
        document.save(output_path)

        # Return the file as a response
        return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f"{clearance_request.document_type}_{clearance_request.full_name}.docx")
    except Exception as e:
        messages.error(request, f"An error occurred while generating the document: {str(e)}")
        return redirect('admin_dashboard')



def history(request):
    search_query = request.GET.get('search', '')

    # Filter requests based on the search query
    if search_query:
        approved_requests = ClearanceRequest.objects.filter(
            Q(status='Approved') &
            (Q(full_name__icontains=search_query) |
             Q(purpose__icontains=search_query) |
             Q(date_requested__icontains=search_query))
        )
        declined_requests = ClearanceRequest.objects.filter(
            Q(status='Declined') &
            (Q(full_name__icontains=search_query) |
             Q(purpose__icontains=search_query) |
             Q(date_requested__icontains=search_query))
        )
    else:
        approved_requests = ClearanceRequest.objects.filter(status='Approved')
        declined_requests = ClearanceRequest.objects.filter(status='Declined')

    return render(request, 'history.html', {
        'approved_requests': approved_requests,
        'declined_requests': declined_requests,
        'title': 'History',
    })

























@login_required
def user_dashboard(request):
    if not request.user.is_approved or request.user.user_type != 'user':
        messages.warning(request, "You don't have permission to access the user dashboard.")
        return redirect('landing_page')
    
    user_requests = ClearanceRequest.objects.filter(user=request.user).order_by('-date_requested')
    approved_requests = user_requests.filter(status='Approved', notification_sent=False)
    
    for req in approved_requests:
        req.notification_sent = True
        req.save()
    
    context = {
        'user_requests': user_requests,
        'approved_requests': approved_requests,
    }
    return render(request, 'dashboard/user_dashboard.html', context)



def user_logout(request):
    logout(request)
    return redirect('landing_page')

# @user_passes_test(lambda u: u.is_superuser)
# def approve_users(request):
#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         action = request.POST.get('action')
#         try:
#             user = CustomUser.objects.get(id=user_id)
#             if action == 'approve':
#                 user.is_approved = True
#                 user.save()
#                 messages.success(request, f"User {user.email} has been approved.")
#             elif action == 'reject':
#                 user.delete()
#                 messages.success(request, f"User {user.email} has been rejected and deleted.")
#         except CustomUser.DoesNotExist:
#             messages.error(request, "User not found.")
#     pending_users = CustomUser.objects.filter(is_approved=False)
#     return render(request, 'my_login/approve_users.html', {'pending_users': pending_users})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')  # Ensure only admins can access
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

    # Separate pending and approved users
    pending_users = CustomUser.objects.filter(is_approved=False)
    approved_users = CustomUser.objects.filter(is_approved=True)

    return render(request, 'approve_users.html', {
        'pending_users': pending_users,
        'approved_users': approved_users,
    })

def approve_request(request, pk):
    clearance_request = get_object_or_404(ClearanceRequest, pk=pk)

    if clearance_request.status == 'Pending':
        pdf_path = generate_document(clearance_request)
        clearance_request.status = 'Approved'
        clearance_request.save()

        # Notify the user
        Notification.objects.create(
            user=clearance_request.user,
            message=f"Your request for {clearance_request.document_type} has been approved.",
        )

    return redirect('admin_dashboard')

def decline_request(request, pk):
    clearance_request = get_object_or_404(ClearanceRequest, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        clearance_request.status = 'Declined'
        clearance_request.decline_reason = reason
        clearance_request.save()

        # Notify the user
        Notification.objects.create(
            user=clearance_request.user,
            message=f"Your request for {clearance_request.document_type} has been declined. Reason: {reason}",
        )

    return redirect('admin_dashboard')

@login_required
def barangay_clearance(request):
    if request.method == "POST":
        # Extract form data
        data = {
            'full_name': f"{request.POST.get('firstname')} {request.POST.get('middlename')} {request.POST.get('lastname')}",
            'address': request.POST.get('address'),
            'birthplace': request.POST.get('birthplace'),
            'birthdate': request.POST.get('birthdate'),
            'civil_status': request.POST.get('civil_status'),
            'gender': request.POST.get('gender'),
            'block_number': request.POST.get('block_number'),
            'occupation': request.POST.get('occupation'),
            'email': request.POST.get('email'),
            'contact': request.POST.get('contact'),
            'purpose': request.POST.get('purpose'),
            'document_type': request.POST.get('document_type'),
        }

        # Check if all required fields are filled
        required_fields = ['full_name', 'address', 'birthplace', 'birthdate', 'civil_status', 'gender', 'block_number', 'occupation', 'email', 'contact', 'purpose', 'document_type']
        if all(data[field] for field in required_fields):
            # Handle file uploads
            profile_photo = request.FILES.get('profile_photo')
            proof_files = request.FILES.getlist('proof_file')

            # Create ClearanceRequest instance
            clearance_request = ClearanceRequest(
                user=request.user,
                **data
            )

            if profile_photo:
                clearance_request.profile_photo = profile_photo

            clearance_request.save()

            # Handle multiple proof of residency files
            for proof_file in proof_files:
                ProofOfResidency.objects.create(file=proof_file, clearance_request=clearance_request)

            messages.success(request, "Your document request has been submitted successfully.")
            return redirect('user_dashboard')
        else:
            messages.error(request, "All fields are required. Please fill in all the information.")
    
    return render(request, 'barangay_clearance_form.html')


@require_POST
@login_required
def update_request_status(request, request_id):
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to update request status.")
        return redirect('landing_page')

    clearance_request = get_object_or_404(ClearanceRequest, id=request_id)
    new_status = request.POST.get("status")
    if new_status in ['Approved', 'Declined']:
        clearance_request.status = new_status
        clearance_request.save()
        messages.success(request, f"Request status updated to {new_status}.")
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



def get_request_details(request, request_id):
    clearance_request = get_object_or_404(ClearanceRequest, id=request_id)
    profile_photo_url = clearance_request.profile_photo.url if clearance_request.profile_photo else None
    proof_of_residency_files = clearance_request.proof_of_residency if clearance_request.proof_of_residency else None # Update this if multiple files are stored differently

    return render(request, 'dashboard/request_details_modal.html', {
        'request': clearance_request,
        'profile_photo_url': profile_photo_url,
        'proof_of_residency_files': proof_of_residency_files,
    })
