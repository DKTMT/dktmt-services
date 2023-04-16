from django.urls import path
from .views import SchedulePredictView

urlpatterns = [
    path('schedule_predict', SchedulePredictView.as_view()),
]
