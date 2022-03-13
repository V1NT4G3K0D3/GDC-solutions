"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

from django.contrib.auth.views import LogoutView
from tasks.tasks import test_background_jobs

from tasks.views import (
    GenericAllTaskView,
    GenericCompletedTaskView,
    GenericTaskCompleteView,
    GenericTaskCreateView,
    GenericTaskDeleteView,
    GenericTaskDetailView,
    GenericTaskUpdateView,
    GenericTaskView,
    GenericCompletedTaskView,
    GenericAllTaskView,
    GenericDeletedTaskView,
    UserCreateView,
    UserLoginView,
    session_storage_view,
    RootPage,
    MailPreferenceView,
)


from rest_framework_nested import routers
from tasks.apiviews import TaskViewSet, TaskStatusViewSet

router = routers.SimpleRouter()
router.register(r"tasks", TaskViewSet)

tasks_router = routers.NestedSimpleRouter(router, r"tasks", lookup="task")
tasks_router.register(r"taskstatus", TaskStatusViewSet, basename="task-status")


def test_bg(request):
    test_background_jobs.delay()
    return HttpResponse("All good here")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RootPage),
    path("form-tasks/", GenericAllTaskView.as_view()),
    path("form-tasks/pending", GenericTaskView.as_view()),
    path("form-tasks/completed", GenericCompletedTaskView.as_view()),
    path("form-tasks/deleted", GenericDeletedTaskView.as_view()),
    path("form-create-task/", GenericTaskCreateView.as_view()),
    path("form-update-task/<pk>", GenericTaskUpdateView.as_view()),
    path("form-detail-task/<pk>", GenericTaskDetailView.as_view()),
    path("form-delete-task/<pk>", GenericTaskDeleteView.as_view()),
    path("form-complete-task/<pk>", GenericTaskCompleteView.as_view()),
    path("form-completed-tasks/", GenericCompletedTaskView.as_view()),
    path("form-all-tasks/", GenericAllTaskView.as_view()),
    path("form-email-preferences/<pk>", MailPreferenceView.as_view()),
    path("sessiontest/", session_storage_view),
    path("user/signup/", UserCreateView.as_view()),
    path("user/login/", UserLoginView.as_view()),
    path("user/logout/", LogoutView.as_view()),
    path(r"", include(router.urls)),
    path(r"", include(tasks_router.urls)),
    path("test-bg", test_bg),
] + router.urls
