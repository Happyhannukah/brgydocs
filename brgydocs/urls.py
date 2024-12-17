from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mambaling.urls')),  # Main app
    path('admin-dashboard/', include('mambaling.urls')),  # Admin dashboard routes
]
