from django.urls import path
from .views import PredictView, StrategyView, BacktestView

urlpatterns = [
    path('run', PredictView.as_view()),
    path('strategy', StrategyView.as_view()),
    path('backtest', BacktestView.as_view()),
]