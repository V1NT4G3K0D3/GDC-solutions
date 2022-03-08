from django.db import models

from django.contrib.auth.models import User
from bulk_update_or_create import BulkUpdateOrCreateQuerySet


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
