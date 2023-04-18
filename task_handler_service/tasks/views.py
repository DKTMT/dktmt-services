import hashlib
import hmac
import requests
import json

from django.http import JsonResponse, HttpResponse

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from task_handler_service.settings import TASK_HANDLER_SERVICE_HOST, TASK_HANDLER_SERVICE_PORT, EXCHANGE_SERVICE_HOST, EXCHANGE_SERVICE_PORT, PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT, NOTIFY_SERVICE_HOST, NOTIFY_SERVICE_PORT, ENCRYPTION_KEY
from task_handler_service.celery import app

from .models import Ticket
from .tasks import schedule_prediction_task


predict_service_url = "http://" + PREDICT_SERVICE_HOST + ":" + PREDICT_SERVICE_PORT
exchange_service_url = "http://" + EXCHANGE_SERVICE_HOST + ":" + EXCHANGE_SERVICE_PORT
notify_service_url = "http://" + NOTIFY_SERVICE_HOST + ":" + NOTIFY_SERVICE_PORT


def hash(data):
    """Hash the data using hmac""" 
    return hmac.new(bytes(ENCRYPTION_KEY, 'utf-8'),
                    bytes(data, 'utf-8'),
                    digestmod=hashlib.sha256).hexdigest()

class SchedulePredictView(APIView):
    def post(self, request):
        body = request.data

        validate_response = requests.get(
            url=f'{notify_service_url}/api/notify/line_notify/validate',
            json={"user_data": json.loads(request.headers['X-User-Data'])},
            headers=request.headers)
        if validate_response.status_code != 200:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        required_keys = {'symbol', 'timeframe', 'exchange', 'strategies', 'duration', 'period', 'name', 'mode'}
        if not required_keys.issubset(body.keys()):
            return HttpResponse("Missing required keys in the request body", status=status.HTTP_400_BAD_REQUEST)

        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get('email')
        hashed_email = hash(email)

        ticket = Ticket(created_by=hashed_email, status='open', **body)
        ticket.save()

        user_data = json.loads(request.headers['X-User-Data'])

        task = schedule_prediction_task.apply_async(args=[ticket.id, user_data])
        ticket.task_id = task.id
        ticket.save()

        response_data = {'message': f'Task scheduled successfully. Ticket ID: {ticket.id}'}
        return HttpResponse(json.dumps(response_data), content_type='application/json', status=status.HTTP_200_OK)

    def put(self, request):
        # Get the request data
        name = request.data.get('name')
        new_status = request.data.get('status')

        # Get the user's hashed email
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get('email')
        hashed_email = hash(email)

        # Update the Ticket object
        try:
            ticket = Ticket.objects.get(name=name, created_by=hashed_email)
            ticket.status = new_status
            ticket.save()

            if new_status == 'open':
                task = schedule_prediction_task.apply_async(args=[ticket.id, json.loads(request.headers['X-User-Data'])])
                ticket.task_id = task.id
                ticket.save()
            elif new_status in ['pause', 'close']:
                if ticket.task_id:
                    app.control.revoke(ticket.task_id, terminate=True)
                    ticket.task_id = None
                    ticket.save()

            data = {'message': f"Ticket {name} status updated to {new_status}"}
            return JsonResponse(data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return JsonResponse({'message': f"Ticket {name} not found or does not belong to the user"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        # Get the user's hashed email
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get('email')
        hashed_email = hash(email)
        
        strategies_response = requests.get(
            url=f'{predict_service_url}/api/predict/strategy/all',
            json={"user_data": json.loads(request.headers['X-User-Data'])},
            headers=request.headers)
        strategies =  strategies_response.json()["strategies"]

        # Retrieve the user's tickets
        tickets = Ticket.objects.filter(created_by=hashed_email)
        ticket_list = []
        for ticket in tickets:
            ticket_list.append({
                'name': ticket.name,
                'duration': ticket.duration,
                'period': ticket.period,
                'symbol': ticket.symbol,
                'timeframe': ticket.timeframe,
                'exchange': ticket.exchange,
                'mode': ticket.mode,
                'strategies': [next((item["name"] for item in strategies if item["id"] == search_id), None) for search_id in ticket.strategies],
                'status': ticket.status,
                'created_at': ticket.created_at,
                'updated_at': ticket.updated_at,
            })

        ticket_list = sorted(ticket_list, key=lambda k: k['name'])

        response_data = {'tickets': ticket_list}
        return JsonResponse(response_data, status=status.HTTP_200_OK)

    def delete(self, request):
        # Get the user's hashed email
        user_data = json.loads(request.headers['X-User-Data'])
        email = user_data.get('email')
        hashed_email = hash(email)

        name = request.data["name"]

        # Delete the Ticket object
        try:
            ticket = Ticket.objects.get(name=name, created_by=hashed_email)
            app.control.revoke(ticket.task_id, terminate=True)
            ticket.delete()
            message = f"Ticket {name} deleted successfully"
            return JsonResponse({'message': message}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            message = f"Ticket {name} not found or does not belong to the user"
            return JsonResponse({'message': message}, status=status.HTTP_404_NOT_FOUND)
