import hmac
import hashlib

from django.http import JsonResponse, HttpResponseRedirect

from rest_framework.views import APIView

from notify_service.settings import ENCRYPTION_KEY, LINE_NOTIFY_CLIENT_ID, LINE_NOTIFY_CLIENT_SECRET, LINE_NOTIFY_REDIRECT_URI
from .line_notify import LineNotify
from .models import AccessToken

def hash(data):
    """Hash the data using hmac"""
    return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                    bytes(data, 'utf-8'),
                    digestmod=hashlib.sha256).hexdigest()

class AccessTokenView(APIView):
    def get(self, request):
        email = request.user_data["email"]
        hashed_email = hash(email)
        try:
            access_token_obj = AccessToken.objects.get(hashed_email=hashed_email)
            return JsonResponse({"result": True})
        except AccessToken.DoesNotExist:
            return JsonResponse({"result": False})

class GenerateAuthorizationURLView(APIView):
    def get(self, request, *args, **kwargs):
        email = request.user_data["email"]
        hashed_email = hash(email)
        auth_url = LineNotify.generate_authorization_url(hashed_email)
        return JsonResponse({"auth_url": auth_url})


class CallbackView(APIView):
    def post(self, request):
        code = request.POST.get("code")
        hashed_email = request.POST.get("state")
        if code is None or hashed_email is None:
            return JsonResponse({"error": "Invalid request."})

        line_notify = LineNotify(
            client_id=LINE_NOTIFY_CLIENT_ID,
            client_secret=LINE_NOTIFY_CLIENT_SECRET,
            redirect_uri=LINE_NOTIFY_REDIRECT_URI,
        )

        access_token = line_notify.get_access_token(code)

        if access_token:
            self.save_access_token_to_user(hashed_email, access_token)
            welcome_message = (
                "Welcome to DKTMT! We are excited to have you join our community and "
                "look forward to providing you with real-time trading predictions and "
                "notifications to help you make informed investment decisions."
            )
            LineNotify.send_message(access_token, welcome_message)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"error": "Failed to get access token."})

    def save_access_token_to_user(self, hashed_email, access_token):
        AccessToken.objects.update_or_create(
            hashed_email=hashed_email, defaults={"access_token": access_token}
        )

class SendMessageView(APIView):
    def post(self, request):
        email = request.user_data["email"]
        hashed_email = AccessToken.hash_email(email)

        try:
            access_token_obj = AccessToken.objects.get(hashed_email=hashed_email)
        except AccessToken.DoesNotExist:
            return JsonResponse({"error": "Access token not found."})

        message = request.data.get("message")

        if not message:
            return JsonResponse({"error": "Message is required."})

        try:
            LineNotify.send_message(access_token_obj.access_token, message)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)})