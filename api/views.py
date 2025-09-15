import logging

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from PIL import Image

from .serializers import (
    UserLoginSerializer, UserRegisterSerializer, UserActionLogSerializer,
    EventSerializer, GuestSerializer, FileUploadSerializer,
    FileUploadGuestSerializer, EventGuestSerializer, AttendanceSerializer, SendLogSerializer,QRReaderSerializer
)
from .models import Event, Guest, FileUpload, FileUploadGuest, EventGuest, Attendance, SendLog

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

class EventListCreateAPIView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class GuestListCreateAPIView(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class GuestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class FileUploadListCreateAPIView(generics.ListCreateAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer

class FileUploadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer

class FileUploadGuestListCreateAPIView(generics.ListCreateAPIView):
    queryset = FileUploadGuest.objects.all()
    serializer_class = FileUploadGuestSerializer

class FileUploadGuestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FileUploadGuest.objects.all()
    serializer_class = FileUploadGuestSerializer

class EventGuestListCreateAPIView(generics.ListCreateAPIView):
    queryset = EventGuest.objects.all()
    serializer_class = EventGuestSerializer

class EventGuestRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EventGuest.objects.all()
    serializer_class = EventGuestSerializer

class AttendanceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class AttendanceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

class SendLogListCreateAPIView(generics.ListCreateAPIView):
    queryset = SendLog.objects.all()
    serializer_class = SendLogSerializer

class SendLogRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SendLog.objects.all()
    serializer_class = SendLogSerializer

class QRContentReviewAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        qr_data = request.data.get("qr_data")
        if not qr_data:
            return Response({"status_code":"MISSING_QR_DATA", "detail": "Falta el parámetro 'qr_data'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document_id,event_id = qr_data.split("#")

            # Buscar al invitado por el ID del QR
            guest = Guest.objects.get(document_id=document_id)
            
            # Buscar la relación EventGuest para este invitado
            event_guest = EventGuest.objects.filter(guest=guest,event_id=event_id).first()

            if event_guest is None:
                return Response({"status_code":"GUEST_NOT_IN_EVENT", "detail": "El invitado no está asociado a este evento."}, status=status.HTTP_200_OK)
            
            # Registrar o actualizar la asistencia
            attendance, created = Attendance.objects.get_or_create(
                event_guest=event_guest,
                defaults={'attended': True}
            )
            if not created:
                # Si ya existía, se asegura de que attended sea True
                attendance.attended = True
                attendance.save()
            
            return Response({
                "status_code":"ATTENDANCE_REGISTERED",
                "message": f"Asistencia registrada para el invitado {guest.name} con ID {document_id}",
                "attended": attendance.attended
            }, status=status.HTTP_200_OK)

        except Guest.DoesNotExist:
            return Response({"status_code":"GUEST_NOT_FOUND", "detail": f"No se encontró un invitado registrado con ese ID de documento."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Error al procesar el QR: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GuestVerifyEventAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        document_id = request.query_params.get('document_id')
        event_id = request.query_params.get('event_id')

        if not document_id or not event_id:
            return Response(
                {"status_code":"MISSING_PARAMS" ,"detail": "Faltan parámetros: 'document_id' y 'event_id' son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            event = Event.objects.get(id=event_id)
            guest = Guest.objects.get(document_id=document_id)
        except Event.DoesNotExist:
            return Response({"status_code":"EVENT_NOT_FOUND" ,"detail": "No se encontró el evento."}, status=status.HTTP_404_NOT_FOUND)
        except Guest.DoesNotExist:
            return Response({"status_code":"GUEST_NOT_FOUND" ,"detail": "No se encontró un invitado registrado con ese ID de documento."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            event_guest = EventGuest.objects.get(guest=guest, event=event)
        except EventGuest.DoesNotExist:
            guest_data = GuestSerializer(guest).data
            return Response(
                {"status_code":"GUEST_NOT_IN_EVENT", "detail": "El invitado no está asociado a este evento.", "guest": guest_data},
                status=status.HTTP_404_NOT_FOUND
            )

        attendance, created = Attendance.objects.get_or_create(
            event_guest=event_guest,
            defaults={'attended': True}
        )
        if not created and not attendance.attended:
            attendance.attended = True
            attendance.save()
        
        return Response({
            "message": f"Asistencia registrada para el invitado {guest.name} con ID {document_id}",
            "attended": attendance.attended,
            "guest_name": guest.name
        }, status=status.HTTP_200_OK)