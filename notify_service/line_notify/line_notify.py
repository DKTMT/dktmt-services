import requests
from django.conf import settings
from urllib.parse import urlencode

class LineNotify:
    LINE_NOTIFY_AUTH_URL = "https://notify-bot.line.me/oauth/authorize"
    LINE_NOTIFY_TOKEN_URL = "https://notify-bot.line.me/oauth/token"
    LINE_NOTIFY_API_URL = "https://notify-api.line.me/api/notify"

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def request_access_token(self, code):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.LINE_NOTIFY_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_access_token(self, code):
        access_token_response = self.request_access_token(code)
        access_token = access_token_response.get("access_token")
        return access_token
    
    @classmethod
    def generate_authorization_url(cls, email):
        params = {
            "response_type": "code",
            "client_id": settings.LINE_NOTIFY_CLIENT_ID,
            "redirect_uri": settings.LINE_NOTIFY_REDIRECT_URI,
            "scope": "notify",
            "state": email,
            "response_mode": "form_post",
        }
        encoded_params = urlencode(params, safe=':/')
        url = f"{cls.LINE_NOTIFY_AUTH_URL}?{encoded_params}"
        return url

    @classmethod
    def send_message(cls, access_token, message):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"message": message}
        response = requests.post(cls.LINE_NOTIFY_API_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    