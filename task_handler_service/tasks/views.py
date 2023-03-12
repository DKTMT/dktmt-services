import json
import requests

from rest_framework.views import APIView
from rest_framework.response import Response

from task_handler_service.settings import PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT

predict_service_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT

class StrategyView(APIView):
    def get(self, request):
        response = requests.request(
                method=request.method, url=predict_service_url + "/api/predict/strategy", headers=request.headers, data=request.body)
        return Response(json.loads(response.content), status=response.status_code)
    
class PredictView(APIView):
    # params 1.coin 2.timeframe 3.exchange
    def get(self, request):
        response = requests.request(
                method=request.method, url=predict_service_url + "/api/predict/run", headers=request.headers, data=request.body)
        return Response(json.loads(response.content), status=response.status_code)
    
class TradeView(APIView):
    # get all ongoing trading jobs
    def get(self, request):
        response = requests.request(
                method=request.method, url=predict_service_url + "/api/exchange/orders", headers=request.headers, data=request.body)
        return Response(response.content, status=response.status_code)

    # params 1.coin(s) 2.timeframe, 3.exchange, 4.duration (times (e.g. 3 times) / range (e.g., 3 days)), 5.conditions (cutloss)
    def post(self, request):
        return Response()

