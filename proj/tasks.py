from celery import shared_task
from time import sleep
# from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json
from webpush import send_user_notification
from django.contrib.auth.models import User

@shared_task
def notify(username, task_name, task_description):
    payload = {"head": task_name, "body": task_description, "icon": "https://assets-global.website-files.com/64de42d1d7652014d6853b95/655f2631ba9dcaececab6392_Google_Tasks_2021.svg.png"}
    send_user_notification(user=User.objects.get(username=username), payload=payload, ttl=1000)
    print(f"{username} - {task_name}")

