import time
import json
import requests

from celery import shared_task

from rest_framework import status

from .models import Ticket

from task_handler_service.settings import PREDICT_SERVICE_HOST, PREDICT_SERVICE_PORT, NOTIFY_SERVICE_HOST, NOTIFY_SERVICE_PORT, TASK_HANDLER_SERVICE_HOST, TASK_HANDLER_SERVICE_PORT

timeframe_lookup = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "2h": 120,
    "4h": 240,
    "6h": 360,
    "8h": 480,
    "12h": 720,
    "1d": 1440,
    "3d": 4320,
    "1w": 10080,
    "1M": 43200,
}

@shared_task
def schedule_prediction_task(ticket_id, user_data):
    ticket = Ticket.objects.get(pk=ticket_id)

    start_time = time.time()
    duration = int(timeframe_lookup.get(ticket.duration)) * 60  # Assuming the duration is in minutes
    period = int(timeframe_lookup.get(ticket.period)) * 60  # Assuming the period is in minutes

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
    strategy_url = f'{predict_service_url}/api/predict/strategy/all'

    headers = {
        'X-User-Data': json.dumps(user_data),
        'Content-type': 'application/json',
    }
    predict_response = requests.post(url=predict_url, json=combined_data, headers=headers)

    strategies_response = requests.get(url=strategy_url, json=combined_data, headers=headers)
    strategies = strategies_response.json()["strategies"]

    if predict_response.status_code == status.HTTP_200_OK:
        predict_data = predict_response.json()["results"]

        notify_url = f'{notify_service_url}/api/notify/line_notify/send_message/'

        combined_data = {'message': f'From Ticket: [[ {ticket.name} ]] of {ticket.symbol} ({ticket.timeframe} timeframe)'}
        combined_data['user_data'] = user_data
        notify_response = requests.post(url=notify_url, json=combined_data, headers=headers)
        for predict_result in predict_data:
            if (predict_result["result"] == ticket.mode or ticket.mode == "all"):
                strategy = next((item for item in strategies if item["id"] == ticket.strategies), None),
                combined_data = {'message': f'{predict_result["name"]} predicted to...{predict_result["result"].upper()}'}
                combined_data['user_data'] = user_data
                notify_response = requests.post(url=notify_url, json=combined_data, headers=headers)

    return predict_response.status_code
