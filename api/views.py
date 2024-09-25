from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserLoginSerializer

class UserLoginAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")

        data = {
            "email": email,
        }
        
        serializer = UserLoginSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "name": str(user.name),
            "last_name": str(user.last_name),
            "id_user": str(user.id),
        }, status=status.HTTP_200_OK)