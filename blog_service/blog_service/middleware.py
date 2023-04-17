import requests
import json
from django.http import HttpResponse, HttpResponseBadRequest

from blog_service.settings import AUTH_SERVICE_PORT, AUTH_SERVICE_HOST

class OAuthValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        validate_url = "http://" + AUTH_SERVICE_HOST + ":" + AUTH_SERVICE_PORT + "/api/auth/validate"
        try:
            response = requests.request(method="GET", url=validate_url, headers=request.headers)
            request.user_data = json.loads(response.content)
            if (response.status_code != 200):
                return HttpResponse('Unauthorized', status=401)
        except:
            return HttpResponseBadRequest('Bad request')
        response = self.get_response(request)
        return response