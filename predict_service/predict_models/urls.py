from django.urls import path
from .views import PredictView, StrategyView

urlpatterns = [
    path('run', PredictView.as_view()),
    path('strategy', StrategyView.as_view()),
]