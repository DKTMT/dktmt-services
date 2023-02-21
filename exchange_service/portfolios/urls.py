from django.urls import path
from .views import PortChangesView

urlpatterns = [
    path('port', PortChangesView.as_view()),
]