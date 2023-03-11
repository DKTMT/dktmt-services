from django.urls import path
from .views import StrategyView, PredictView, TradeView

urlpatterns = [
    path('strategy', StrategyView.as_view()),
    path('predict', PredictView.as_view()),
    path('trade', TradeView.as_view()),
]