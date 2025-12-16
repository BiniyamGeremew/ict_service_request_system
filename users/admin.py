from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    readonly_fields = ('date_joined',)

    model = CustomUser
    list_display = ('username', 'email', 'department', 'staff_id', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('department', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'staff_id', 'department')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'department', 'staff_id', 'phone_number', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('username', 'email', 'staff_id')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
