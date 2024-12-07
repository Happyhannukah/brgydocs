from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.my_login, name='my_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('register/user/', views.user_register, name='user_register'),
    path('approve-users/', views.approve_users, name='approve_users'),
]

