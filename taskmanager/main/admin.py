from django.contrib import admin
from .models import Task, User, Role, Product, Plan
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Создание/изменение планов пользователя в админ-панели
class PlanInline(admin.TabularInline):
    model = Plan
    extra = 0
    fk_name = 'User'

# Управление моделью пользователя
class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ['id', 'username', 'last_name', 'first_name', 'middle_name', 'role', 'email', 'phone_number', 'telegram', 'vk', 'is_staff']
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role', 'last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'telegram', 'vk', 'is_staff', 'is_superuser',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'last_name', 'first_name', 'middle_name', 'email', 'phone_number', 'telegram', 'vk', 'is_staff', 'is_superuser'),
        }),
    )
    inlines = [PlanInline]

# Регистрация роли и пользователя в админ-панели
admin.site.register(Task)
admin.site.register(Role)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Product)