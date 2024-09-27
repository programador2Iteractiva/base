import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserLoginSerializer, UserRegisterSerializer, UserActionLogSerializer

logger = logging.getLogger('user_actions')

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        data = {
            "email": email,
        }
        
        serializer = UserLoginSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        logger.info(f"Login", extra={'user': user})

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "name": str(user.name),
            "last_name": str(user.last_name),
            "id_user": str(user.id),
        }, status=status.HTTP_200_OK)

class UserRegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email")
        name = request.data.get("name")
        last_name = request.data.get("last_name")
        data = {
            "name": name,
            "last_name": last_name,
            "email": email,
        }

        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Registro del usuario {email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserActionLogCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserActionLogSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = request.user if request.user.is_authenticated else None
            action = serializer.validated_data.get('action', 'Acción sin especificar')
            
            logger.info(action, extra={'user': user})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)