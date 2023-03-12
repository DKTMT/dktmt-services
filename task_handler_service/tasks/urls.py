from django.urls import path
from .views import StrategyView, PredictView, TradeView

urlpatterns = [
    path('predict/strategy', StrategyView.as_view()),
    path('predict/run', PredictView.as_view()),
    path('trade', TradeView.as_view()),
]