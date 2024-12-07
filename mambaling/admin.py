from django.contrib import admin
from .models import CustomUser


# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'is_active', 'is_approved')
#     list_filter = ('is_active', 'is_approved')
#     actions = ['approve_users']

#     def approve_users(self, request, queryset):
#         queryset.update(is_active=True, is_approved=True)
#         self.message_user(request, "Selected users have been approved.")
#     approve_users.short_description = "Approve selected users"

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type')
    list_filter = ('user_type',)