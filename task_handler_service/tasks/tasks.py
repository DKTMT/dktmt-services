import time
import json
import requests

from celery import shared_task

from rest_framework import status

from .models import Ticket

from task_handler_service.settings import PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT, NOTIFY_SERVICE_HOST, NOTIFY_SERVICE_PORT

@shared_task
def schedule_prediction_task(ticket_id, user_data):
    ticket = Ticket.objects.get(pk=ticket_id)

    start_time = time.time()
    duration = int(ticket.duration) * 60  # Assuming the duration is in minutes
    period = int(ticket.period) * 60  # Assuming the period is in minutes

    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        ticket.refresh_from_db()
        if elapsed_time >= duration or ticket.status == 'close' or ticket.status == 'pause':
            ticket.status = 'close'
            ticket.save()
            break

        run_prediction_and_notify_task(ticket, user_data)

        time.sleep(period)

@shared_task
def run_prediction_and_notify_task(ticket, user_data):
    print ("run_prediction_and_notify_task called")
    predict_service_url = f"http://{PREDICT_SERVICE_HOST}:{PREDICT_SERVICE_PORT}"
    notify_service_url = f"http://{NOTIFY_SERVICE_HOST}:{NOTIFY_SERVICE_PORT}"

    body = {
        'symbol': ticket.symbol,
        'timeframe': ticket.timeframe,
        'exchange': ticket.exchange,
        'strategies': ticket.strategies
    }

    combined_data = body.copy()
    combined_data['user_data'] = user_data

    predict_url = f'{predict_service_url}/api/predict/run'

    headers = {
        'Host': f"{PREDICT_SERVICE_HOST}:{PREDICT_SERVICE_PORT}",
        'Content-Type': 'application/json',
        'X-Task-Handler': 'True'
    }

    predict_response = requests.post(url=predict_url, json=combined_data, headers=headers)

    print (predict_response)

    if predict_response.status_code == status.HTTP_200_OK:
        predict_data = predict_response.json()
        pretty_predict_data = json.dumps(predict_data, indent=4, sort_keys=True)

        notify_url = f'{notify_service_url}/api/notify/line_notify/send_message/'
        notify_response = requests.post(url=notify_url, json={'message': pretty_predict_data})

    return predict_response.status_code
