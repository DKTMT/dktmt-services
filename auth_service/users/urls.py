from django.urls import path
from .views import RegisterView, LoginView, ValidateView, LogoutView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('validate', ValidateView.as_view()),
]