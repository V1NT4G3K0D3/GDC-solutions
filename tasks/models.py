from django.db import models

from django.contrib.auth.models import User
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from django.db.models.signals import pre_save, post_save

STATUS_CHOICES = (
    ("PENDING", "PENDING"),
    ("IN_PROGRESS", "IN_PROGRESS"),
    ("COMPLETED", "COMPLETED"),
    ("CANCELLED", "CANCELLED"),
)


class Task(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=False
    )
    priority = models.IntegerField(null=True, blank=False)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == "COMPLETED":
            self.completed = True
        super(Task, self).save(*args, **kwargs)


class TaskStatusChanges(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )


# Signals


def push_data(priority, next_task):
    update_tasks = []
    while True:
        if next_task:
            priority += 1
            next_task.priority = priority
            update_tasks.append(next_task)
            next_task = Task.objects.filter(
                priority=priority,
                user=next_task.user,
                deleted=False,
                completed=False,
            ).first()
        else:
            break

    Task.objects.bulk_update_or_create(
        update_tasks, ["priority"], match_field=["id"]
    )


def task_pre_save_signal(sender, instance, **kwargs):
    if instance.status == "COMPLETED":
        instance.completed = True
    else:
        instance.completed = False

    if instance.priority:
        next_task = Task.objects.filter(
            priority=instance.priority,
            user=instance.user,
            deleted=False,
            completed=False,
        ).first()

        if next_task:
            push_data(instance.priority, next_task)


def task_post_save_signal(sender, instance, **kwargs):
    print(instance)
    print(sender)
    print(f" Kwargs: {kwargs}")


pre_save.connect(task_pre_save_signal, sender=Task)
post_save.connect(task_post_save_signal, sender=Task)
