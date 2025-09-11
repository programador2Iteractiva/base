from django.urls import path
from .views import (
    UserLoginAPIView, UserRegisterAPIView, UserActionLogCreateAPIView,
    EventListCreateAPIView, EventRetrieveUpdateDestroyAPIView,
    GuestListCreateAPIView, GuestRetrieveUpdateDestroyAPIView,
    FileUploadListCreateAPIView, FileUploadRetrieveUpdateDestroyAPIView,
    FileUploadGuestListCreateAPIView, FileUploadGuestRetrieveUpdateDestroyAPIView,
    AttendanceLogListCreateAPIView, AttendanceLogRetrieveUpdateDestroyAPIView,
    SendLogListCreateAPIView, SendLogRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("user-register/", UserRegisterAPIView.as_view(), name="user-register"),
    path("user-action-log/", UserActionLogCreateAPIView.as_view(), name='user-action-log-create'),
    # New endpoints
    path("events/", EventListCreateAPIView.as_view(), name="event-list-create"),
    path("events/<int:pk>/", EventRetrieveUpdateDestroyAPIView.as_view(), name="event-detail"),
    path("guests/", GuestListCreateAPIView.as_view(), name="guest-list-create"),
    path("guests/<int:pk>/", GuestRetrieveUpdateDestroyAPIView.as_view(), name="guest-detail"),
    path("file-uploads/", FileUploadListCreateAPIView.as_view(), name="file-upload-list-create"),
    path("file-uploads/<int:pk>/", FileUploadRetrieveUpdateDestroyAPIView.as_view(), name="file-upload-detail"),
    path("file-upload-guests/", FileUploadGuestListCreateAPIView.as_view(), name="file-upload-guest-list-create"),
    path("file-upload-guests/<int:pk>/", FileUploadGuestRetrieveUpdateDestroyAPIView.as_view(), name="file-upload-guest-detail"),
    path("attendance-logs/", AttendanceLogListCreateAPIView.as_view(), name="attendance-log-list-create"),
    path("attendance-logs/<int:pk>/", AttendanceLogRetrieveUpdateDestroyAPIView.as_view(), name="attendance-log-detail"),
    path("send-logs/", SendLogListCreateAPIView.as_view(), name="send-log-list-create"),
    path("send-logs/<int:pk>/", SendLogRetrieveUpdateDestroyAPIView.as_view(), name="send-log-detail"),
]