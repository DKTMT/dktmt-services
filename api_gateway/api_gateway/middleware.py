import requests
import json
from django.http import HttpResponse, HttpResponseBadRequest
from api_gateway.settings import AUTH_SERVICE_PORT, AUTH_SERVICE_HOST, EXCHANGE_SERVICE_PORT, EXCHANGE_SERVICE_HOST, NOTIFY_SERVICE_PORT, NOTIFY_SERVICE_HOST, PREDICT_SERVICE_PORT, PREDICT_SERVICE_HOST, TASK_HANDLER_SERVICE_PORT, TASK_HANDLER_SERVICE_HOST, BLOG_SERVICE_HOST, BLOG_SERVICE_PORT

class OAuthValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = [
            "/api/notify/line_notify/callback/",
        ]

    def is_excluded_path(self, path):
        return path in self.excluded_paths

    def __call__(self, request):
        if self.is_excluded_path(request.path) or request.path.startswith('/api/auth'):
            pass
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

class ReverseProxyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api'):
            # Add user_data to headers
            headers = dict(request.headers)
            if hasattr(request, 'user_data'):
                headers['X-User-Data'] = json.dumps(request.user_data)

            # auth service
            if request.path.startswith('/api/auth'):
                microservice_url = "http://" + AUTH_SERVICE_HOST + ":" + AUTH_SERVICE_PORT + request.path
            # exchange service
            elif request.path.startswith('/api/exchange'):
                microservice_url = "http://" + EXCHANGE_SERVICE_HOST + ":" + EXCHANGE_SERVICE_PORT + request.path
            # task handler service
            elif request.path.startswith('/api/predict'):
                microservice_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT + request.path
            # task handler service
            elif request.path.startswith('/api/task'):
                microservice_url = "http://" + TASK_HANDLER_SERVICE_HOST + ":" + TASK_HANDLER_SERVICE_PORT + request.path
            # notification service
            elif request.path.startswith('/api/notify'):
                microservice_url = "http://" + NOTIFY_SERVICE_HOST + ":" + NOTIFY_SERVICE_PORT + request.path
            # blog service
            elif request.path.startswith('/api/blog'):
                microservice_url = "http://" + BLOG_SERVICE_HOST + ":" + BLOG_SERVICE_PORT + request.path
            else:
                return HttpResponseBadRequest('Bad request')

            query_params = request.GET.urlencode()
            if (query_params):
                microservice_url + "?" + query_params

            print(microservice_url)
            response = requests.request(
                method=request.method, url=microservice_url, headers=headers, data=request.body)
            return HttpResponse(response.content, status=response.status_code)
        else:
            response = self.get_response(request)
            return response
