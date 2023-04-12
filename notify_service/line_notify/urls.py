from django.urls import path
from .views import GenerateQRCodeView, CallbackView

urlpatterns = [
    path('generate_qrcode/', GenerateQRCodeView.as_view(), name='generate_qrcode'),
    path('callback/', CallbackView.as_view(), name='callback'),
]
