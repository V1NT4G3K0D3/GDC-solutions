import time

from tasks.models import User, Task
from django.core.mail import send_mail
from datetime import timedelta, datetime

from task_manager.celery import app
from celery.decorators import periodic_task
from celery.schedules import crontab
from django.utils import timezone


def get_email_content(user):
    email_content = ""
    pending_tasks = Task.objects.filter(
        user=user, completed=False, deleted=False
    )
    completed_tasks = Task.objects.filter(user=user, completed=True)
    deleted_tasks = Task.objects.filter(user=user, deleted=True)
    all_tasks = Task.objects.filter(user=user)

    if user.preference.pending_preference:
        email_content += "\n\nPending Tasks:\n"
        for task in pending_tasks:
            email_content += f"{task.priority}: {task.title}\n"
    if user.preference.completed_preference:
        email_content += "\n\nCompleted Tasks:\n"
        for task in completed_tasks:
            email_content += f"{task.priority}: {task.title}\n"
    if user.preference.deleted_preference:
        email_content += "\n\nDeleted Tasks:\n"
        for task in deleted_tasks:
            email_content += f"{task.priority}: {task.title}\n"
    if user.preference.all_preference:
        email_content += "\n\nAll Tasks:\n"
        for task in all_tasks:
            email_content += f"{task.priority}: {task.title}\n"

    # email_content='\n'.join([f'{key}:: {value}' for key, value in email_content.items()])
    email_content += f"\n\nStatistics: \n\nPending: {pending_tasks.count()} \nCompleted: {completed_tasks.count()} \nDeleted: {deleted_tasks.count()} \nTotal: {all_tasks.count()}"
    print(email_content)
    return email_content


@periodic_task(run_every=timedelta(hours=1))
def send_email_reminder():
    for user in User.objects.all():
        if timezone.now() - user.preference.last_sent_time > timedelta(days=1):
            email_content = get_email_content(user)
            send_mail(
                "TASK MANAGER",
                email_content,
                "post@sandbox7203e0cc672c40ba87ca489dc01d48ea.mailgun.org",
                [user.email],
            )
            user.preference.last_sent_time = timezone.now()
            user.preference.save()


@app.task
def test_background_jobs():
    print("This is from the bg")
    for i in range(10):
        time.sleep(1)
        print(i)
