from django.urls import path
from .views import PredictView, BaseStrategyView, StrategyView, BacktestView, CustomStrategyView

urlpatterns = [
    path('run', PredictView.as_view()),
    path('strategy', BaseStrategyView.as_view()),
    path('strategy/custom', CustomStrategyView.as_view()),
    path('strategy/all', StrategyView.as_view()),
    path('backtest', BacktestView.as_view()),
]