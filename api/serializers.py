from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework.response import Response
from rest_framework import status

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate(self, attrs):
        email = attrs.get("email")
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                msg = "El email no se encuentra registrado."
                raise serializers.ValidationError(msg, code="authorization")
            if user.is_active:
                user = authenticate(request=self.context.get("request"), username=email, password=email)
                if not user:
                    msg = "Las credenciales proporcionadas son incorrectas."
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = "La cuenta de usuario no está activa."
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = "Por favor, proporciona un email."
            raise serializers.ValidationError(msg, code='authorization')

        attrs["user"] = user
        return attrs