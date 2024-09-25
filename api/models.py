from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, **kwargs):
        if not email:
            raise ValueError("Debe tener campo email")

        user = self.model(
            email=email, is_active=is_active, **kwargs
        )
        user.set_password(email)
        user.save(using=self._db)

        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    email = models.EmailField(
        unique=True,
        max_length=200,
        verbose_name="Correo electrónico",
        help_text="""Ten en cuenta que al cambiar el correo electrónico,
        ese sería con el que ingresarías a la plataforma.""",
    )

    name = models.CharField(
        blank=True,
        max_length=200,
        verbose_name="Nombre",
    )

    last_name = models.CharField(
        blank=True,
        max_length=200,
        verbose_name="Apellido",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el usuario puede ser tratado como activo.",
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff",
        help_text="Indica si puede entrar al sitio de administración.",
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    modified = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Actualización"
    )

    objects = UserManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
    
    def __str__(self):
        return self.email