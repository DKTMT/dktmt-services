from django.urls import path
from .views import PortHistoryView, UserAPIView, PortView, OrderView, UserAPIValidateView

urlpatterns = [
    path('api', UserAPIView.as_view()),
    path('api/validate', UserAPIValidateView.as_view()),
    path('port', PortView.as_view()),
    path('port/history', PortHistoryView.as_view()),
    path('order', OrderView.as_view()),
]