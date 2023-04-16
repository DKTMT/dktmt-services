from django.urls import path

from .views import GenerateAuthorizationURLView, CallbackView, SendMessageView, AccessTokenView

urlpatterns = [
    path('generate_auth_url/', GenerateAuthorizationURLView.as_view(), name='generate_auth_url'),
    path("send_message/", SendMessageView.as_view(), name="send_message"),
    path('callback/', CallbackView.as_view(), name='callback'),
    path("validate/", AccessTokenView.as_view(), name="validate")
]
