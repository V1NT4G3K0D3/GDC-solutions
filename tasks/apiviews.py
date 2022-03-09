from urllib import request
from tasks.models import Task, TaskStatusChanges
from tasks.serializers import (
    TaskSerializer,
    TaskStatusSerializer,
)
from tasks.filters import TaskFilter, TaskStatusFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by("priority")

    def perform_create(self, serializer):
        serializer.validated_data["user"] = self.request.user

        data = serializer.save()

        if data.status:
            task_status = TaskStatusChanges(
                task=serializer.instance,
                status=serializer.validated_data["status"],
            )
            task_status.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.validated_data["user"] = self.request.user

        serializer.save()

        if not serializer.validated_data["status"] == instance.status:
            task_status = TaskStatusChanges(
                task=serializer.instance,
                status=serializer.validated_data["status"],
            )
            task_status.save()


class TaskStatusViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TaskStatusSerializer

    permission_class = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskStatusFilter

    def get_queryset(self):
        return TaskStatusChanges.objects.filter(
            task__user=self.request.user,
            task__deleted=False,
            task_id=self.kwargs["task_pk"],
        )
