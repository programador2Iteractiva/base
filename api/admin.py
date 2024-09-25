from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "groups",
    )
    ordering = ["name"]
    readonly_fields = ["date_joined"]
    search_fields = ("name", "email")

    add_fieldsets = (
        (
            "Información básica",
            {
                "fields": (
                    "name",
                    "last_name",
                ),
            },
        ),
        (
            "Información de acceso",
            {
                "fields": (
                    "email",
                ),
            },
        ),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )
    fieldsets = (
        (
            "Información de acceso",
            {
                "fields": (
                    "email",
                ),
            },
        ),
        (
            "Información básica",
            {
                "fields": (
                    "name",
                    "last_name",
                ),
            },
        ),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    class Meta:
        ordering = "name"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
