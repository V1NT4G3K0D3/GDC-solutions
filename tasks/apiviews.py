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
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend


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


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data["status"] == "COMPLETED":
            serializer.validated_data["completed"] = True
        else:
            serializer.validated_data["completed"] = False

        serializer.validated_data["user"] = self.request.user
        next_task = Task.objects.filter(
            priority=serializer.validated_data["priority"],
            user=serializer.validated_data["user"],
            deleted=False,
            completed=False,
        ).first()

        if next_task:
            push_data(serializer.validated_data["priority"], next_task)

        data = serializer.save()

        if data.status:
            task_status = TaskStatusChanges(
                task=serializer.instance,
                status=serializer.validated_data["status"],
            )
            task_status.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        if not serializer.validated_data["status"] == instance.status:
            task_status = TaskStatusChanges(
                task=serializer.instance,
                status=serializer.validated_data["status"],
            )
            task_status.save()
        if serializer.validated_data["status"] == "COMPLETED":
            serializer.validated_data["completed"] = True
        else:
            serializer.validated_data["completed"] = False

        serializer.validated_data["user"] = self.request.user
        next_task = Task.objects.filter(
            priority=serializer.validated_data["priority"],
            user=serializer.validated_data["user"],
            deleted=False,
            completed=False,
        ).first()

        if next_task:
            push_data(serializer.validated_data["priority"], next_task)

        serializer.save()


class TaskStatusViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = TaskStatusSerializer

    permission_class = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskStatusFilter

    def get_queryset(self):
        task = Task.objects.filter(
            id=self.kwargs["task_pk"], user=self.request.user
        ).first()
        if task:
            return TaskStatusChanges.objects.filter(task=task)
        else:
            raise NotFound("Task not found")
