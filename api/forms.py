from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User

class UserCreationForm(forms.ModelForm):
    """Formulario para crear usuarios nuevos sin confirmación de contraseña"""
    
    class Meta:
        model = User
        fields = ('email', 'name', 'last_name')

    def save(self, commit=True):
        # Asignar el email como contraseña automáticamente
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["email"])  # Usar el email como contraseña
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """Formulario para actualizar usuarios existentes"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'name', 'last_name', 'is_active', 'is_staff')

    def clean_password(self):
        # Verifica si el campo password está en self.initial (se usa en formularios de cambio)
        return self.initial.get("password", None)
