from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

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

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "last_name"]

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            name=validated_data["name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["email"])
        user.save()
        return user