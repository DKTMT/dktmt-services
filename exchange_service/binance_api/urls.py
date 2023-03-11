from django.urls import path
from .views import TestView, UserAPIView, PortView, OrderView

urlpatterns = [
    path('test', TestView.as_view()),
    path('api', UserAPIView.as_view()),
    path('port', PortView.as_view()),
    path('order', OrderView.as_view()),
]