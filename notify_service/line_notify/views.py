from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import qrcode
import base64
from io import BytesIO

from notify_service.settings import (
    LINE_NOTIFY_CLIENT_ID,
    LINE_NOTIFY_CLIENT_SECRET,
    LINE_NOTIFY_REDIRECT_URI,
)

from .models import AccessToken

class GenerateQRCodeView(APIView):
    def get(self, request):
        state = "your_state"
        scope = "notify"
        auth_url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={LINE_NOTIFY_CLIENT_ID}&redirect_uri={LINE_NOTIFY_REDIRECT_URI}&state={state}&scope={scope}"
        img = qrcode.make(auth_url)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return Response({"qrcode": img_str})

class CallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")

        if code:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": LINE_NOTIFY_REDIRECT_URI,
                "client_id": LINE_NOTIFY_CLIENT_ID,
                "client_secret": LINE_NOTIFY_CLIENT_SECRET,
            }
            response = requests.post("https://api.line.me/oauth2/v2.1/token", data=data)

            if response.status_code == 200:
                access_token = response.json()['access_token']
                email = request.user_data["email"]
                AccessToken.save_access_token(email, access_token)
                return Response({"detail": "Access token saved successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Error occurred while fetching access token."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Code not found in the request."}, status=status.HTTP_400_BAD_REQUEST)
