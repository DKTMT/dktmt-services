from django.urls import path
from .views import PredictView

urlpatterns = [
    path('predict/<str:task_type>', PredictView.as_view()),
]