from django.contrib import admin
from django.urls import path


from tasks.views import (
    tasks_view,
    add_tasks_view,
    delete_tasks_view,
    complete_task_view,
    completed_tasks_view,
    all_tasks_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tasks/", tasks_view),
    path("add-task/", add_tasks_view),
    path("delete-task/<int:id>/", delete_tasks_view),
    path("complete_task/<int:id>/", complete_task_view),
    path("completed_tasks/", completed_tasks_view),
    path("all_tasks/", all_tasks_view),
]
