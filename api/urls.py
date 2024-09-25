from django.urls import path
from .views import UserLoginAPIView, UserRegisterView

urlpatterns = [
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("user-register/", UserRegisterView, name="user-register"),
]
