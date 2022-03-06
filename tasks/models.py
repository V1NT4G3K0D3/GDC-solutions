from django.db import models

from django.contrib.auth.models import User
from bulk_update_or_create import BulkUpdateOrCreateQuerySet


class Task(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    priority = models.IntegerField(null=True, blank=False)

    def __str__(self):
        return self.title
