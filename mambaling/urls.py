from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
import datetime 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.my_login, name='my_login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('register/user/', views.user_register, name='user_register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-profile/', views.admin_profile, name='admin_profile'),
    path('generate-document/<int:request_id>/', views.generate_final_document, name='generate_final_document'),


    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    


    path('approve-users/', views.approve_users, name='approve_users'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('history/', views.history, name='history'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        name='password_reset_complete'
    ),

    path('approve/<int:pk>/', views.approve_request, name='approve_request'),
    path('decline/<int:pk>/', views.decline_request, name='decline_request'),

    path('barangay-clearance/', views.barangay_clearance, name='barangay_clearance'),
    path('update-request-status/<int:request_id>/', views.update_request_status, name='update_request_status'),
    path('download-clearance/<int:request_id>/', views.download_clearance_pdf, name='download_clearance'),
    path('certificate_requests/', views.certificate_requests, name='certificate_requests'),
    path('get-request-details/<int:request_id>/', views.get_request_details, name='get_request_details'),

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

