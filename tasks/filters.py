from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
)

from django_filters import DateTimeFilter
from tasks.models import STATUS_CHOICES, TaskStatusChanges


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)
    completed = ChoiceFilter(choices=((True, "True"), (False, "False")))


class TaskStatusFilter(FilterSet):
    status = ChoiceFilter(choices=STATUS_CHOICES)
    timestamp_gte = DateTimeFilter(field_name="timestamp", lookup_expr="gte")

    class Meta:
        model = TaskStatusChanges
        fields = ["status", "timestamp", "timestamp_gte"]
