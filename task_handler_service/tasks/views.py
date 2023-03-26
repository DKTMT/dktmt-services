import requests

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from task_handler_service.settings import EXCHANGE_SERVICE_HOST, EXCHANGE_SERVICE_PORT, PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT

predict_service_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT
exchange_service_url = "http://" + EXCHANGE_SERVICE_HOST + ":" + EXCHANGE_SERVICE_PORT


class PredictView(APIView):
    def dispatch(self, request, *args, **kwargs):
        # Construct the URL for the predict_service endpoint
        url = f'{predict_service_url}/api/predict/{kwargs["task_type"]}'

        response = requests.request(
            method=request.method, url=url, headers=request.headers, data=request.body)
        return HttpResponse(response.content, status=response.status_code)

class TradeView(APIView):
    # get all ongoing trading jobs
    def get(self, request):
        response = requests.request(
                method=request.method, url=exchange_service_url + "/api/exchange/orders", headers=request.headers, data=request.body)
        return Response(response.content, status=response.status_code)

    # params 1.coin(s) 2.timeframe, 3.exchange, 4.duration (times (e.g. 3 times) / range (e.g., 3 days)), 5.conditions (cutloss)
    def post(self, request):
        return Response()

