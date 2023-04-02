from celery import shared_task
from apscheduler.schedulers.background import BackgroundScheduler

@shared_task
def run_scheduled_task(params):
    print ("run_scheduled_task called")
    duration = params.get('duration', 3)
    counter = 0
    
    def my_task():
        nonlocal counter
        counter += 1
        print (f'Hello {counter}')
        if counter >= duration:
            scheduler.remove_job('print_job')
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(my_task, 'interval', seconds=3, id='print_job')
    scheduler.start()
