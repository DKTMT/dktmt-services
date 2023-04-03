from django.urls import path
from .views import PredictView, StrategyView, BacktestView, CustomStrategyView

urlpatterns = [
    path('run', PredictView.as_view()),
    path('strategy', StrategyView.as_view()),
    path('backtest', BacktestView.as_view()),
    path('custom-strategy', CustomStrategyView.as_view()),
    path('custom-strategy/<int:pk>', CustomStrategyView.as_view()),
]