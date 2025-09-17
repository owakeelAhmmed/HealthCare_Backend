from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone', 'is_staff', 'is_active')
    list_display_links = ('id', 'username', 'email')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'user_type')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'phone', 'user_type',
                'is_staff', 'is_active'
            ),
        }),
    )

admin.site.register(User, UserAdmin)
