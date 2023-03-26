from django.urls import path
from .views import PredictView, TradeView

urlpatterns = [
    path('predict/<str:task_type>', PredictView.as_view()),
    path('trade', TradeView.as_view()),
]