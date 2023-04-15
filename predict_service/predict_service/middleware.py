import requests
import json
from django.http import HttpResponse, HttpResponseBadRequest

from predict_service.settings import AUTH_SERVICE_PORT, AUTH_SERVICE_HOST, TASK_HANDLER_SERVICE_HOST, TASK_HANDLER_SERVICE_PORT

class OAuthValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print (request.headers.get("HOST"))
        if request.headers.get("HOST") == f'{TASK_HANDLER_SERVICE_HOST}:{TASK_HANDLER_SERVICE_PORT}':
            try:
                request.user_data = json.loads(request.body).get("user_data", {})
            except json.JSONDecodeError:
                print("Invalid JSON data in request.body")
        else:
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