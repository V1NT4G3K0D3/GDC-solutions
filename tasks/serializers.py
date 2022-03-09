from rest_framework.serializers import ModelSerializer
from tasks.models import Task, User, TaskStatusChanges


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
        ]


class TaskSerializer(ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "completed",
            "deleted",
            "user",
            "priority",
            "id",
        ]
        read_only_fields = ["completed", "deleted", "user"]


class TaskSerializerForStatus(ModelSerializer):
    class Meta:
        model = Task
        fields = ["id"]


class TaskStatusSerializer(ModelSerializer):

    task = TaskSerializerForStatus(read_only=True)

    class Meta:
        model = TaskStatusChanges
        fields = ["task", "status", "timestamp"]
        read_only_fields = ["task", "timestamp", "status"]
