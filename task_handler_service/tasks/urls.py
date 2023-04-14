from django.urls import path
from .views import PredictView, SchedulePredictView

urlpatterns = [
    path('predict/<str:task_type>', PredictView.as_view()),
    path('schedule_predict', SchedulePredictView.as_view()),
]
