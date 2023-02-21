import requests
from django.http import HttpResponse, HttpResponseBadRequest
from api_gateway.settings import AUTH_SERVICE_PORT, AUTH_SERVICE_HOST, EXCHANGE_SERVICE_PORT, EXCHANGE_SERVICE_HOST, NOTI_SERVICE_PORT, NOTI_SERVICE_HOST, PREDICT_SERVICE_PORT, PREDICT_SERVICE_HOST, TASK_HANDLE_SERVICE_PORT, TASK_HANDLE_SERVICE_HOST


class ReverseProxyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api'):
            # auth service
            if request.path.startswith('/api/auth'):
                microservice_url = "http://" + AUTH_SERVICE_HOST + ":" + AUTH_SERVICE_PORT + request.path
            # exchange service
            elif request.path.startswith('/api/exchange'):
                microservice_url = "http://" + EXCHANGE_SERVICE_HOST + ":" + EXCHANGE_SERVICE_PORT + request.path
            # task handler service
            elif request.path.startswith('/api/task'):
                microservice_url = "http://" + TASK_HANDLE_SERVICE_HOST + ":" + TASK_HANDLE_SERVICE_PORT + request.path
            # model service
            elif request.path.startswith('/api/predict'):
                microservice_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT + request.path
            # notification service
            elif request.path.startswith('/api/noti'):
                microservice_url = "http://" + NOTI_SERVICE_HOST + ":" + NOTI_SERVICE_PORT + request.path
            else:
                return HttpResponseBadRequest('Bad request')

            # try:
            print (microservice_url)
            response = requests.request(
                method=request.method, url=microservice_url, headers=request.headers, data=request.body)
            return HttpResponse(response.content, status=response.status_code)
            # except:
            #     return HttpResponseBadRequest('Bad request')
        else:
            response = self.get_response(request)
            return response
