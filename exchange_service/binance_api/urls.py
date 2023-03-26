from django.urls import path
from .views import UserAPIView, PortView, OrderView

urlpatterns = [
    path('api', UserAPIView.as_view()),
    path('port', PortView.as_view()),
    path('order', OrderView.as_view()),
]