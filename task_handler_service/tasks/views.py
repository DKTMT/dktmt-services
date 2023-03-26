import requests

from django.http import HttpResponse
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response

from task_handler_service.settings import EXCHANGE_SERVICE_HOST, EXCHANGE_SERVICE_PORT, PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT
from .models import Ticket

predict_service_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT
exchange_service_url = "http://" + EXCHANGE_SERVICE_HOST + ":" + EXCHANGE_SERVICE_PORT

class PredictView(APIView):
    def dispatch(self, request, *args, **kwargs):
        task_type = kwargs["task_type"]
        # Construct the URL for the predict_service endpoint
        url = f'{predict_service_url}/api/predict/{task_type}'
        response = requests.request(
            method=request.method, url=url, headers=request.headers, data=request.body)
        return HttpResponse(response.content, status=response.status_code)
    
class TicketView(APIView):
    def get(self, request):
        performance = 0;
        return Response(performance)
