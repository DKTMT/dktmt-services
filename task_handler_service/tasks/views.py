import requests
import json

from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework import status

from task_handler_service.settings import EXCHANGE_SERVICE_HOST, EXCHANGE_SERVICE_PORT, PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT
from tasks.tasks import run_scheduled_task

predict_service_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT
exchange_service_url = "http://" + EXCHANGE_SERVICE_HOST + ":" + EXCHANGE_SERVICE_PORT

class PredictView(APIView):
    def dispatch(self, request, *args, **kwargs):
        task_type = kwargs["task_type"]
        if (task_type == "schedule"):
            if (request.method == "POST"):
                params = {
                    'duration': 5
                }
                run_scheduled_task.delay(params)
                response_data = {'message': 'Task scheduled successfully.'}
                return HttpResponse(json.dumps(response_data), content_type='application/json', status=status.HTTP_200_OK)
        else:
            url = f'{predict_service_url}/api/predict/{task_type}'
            response = requests.request(
                method=request.method, url=url, headers=request.headers, data=request.body)
            return HttpResponse(response.content, status=response.status_code)
