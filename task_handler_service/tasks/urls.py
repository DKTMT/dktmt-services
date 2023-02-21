from django.urls import path
from .views import StrategyView, PredictView

urlpatterns = [
    path('strategies', StrategyView.as_view()),
    path('predict', PredictView.as_view()),
]