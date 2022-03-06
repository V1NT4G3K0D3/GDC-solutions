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
from django.contrib.auth.views import LogoutView
from django.urls import path, include
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
)
from django.conf import settings
from django.conf.urls.static import static

# from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RootPage),
    path("tasks/", GenericAllTaskView.as_view()),
    path("tasks/pending", GenericTaskView.as_view()),
    path("tasks/completed", GenericCompletedTaskView.as_view()),
    path("tasks/deleted", GenericDeletedTaskView.as_view()),
    path("create-task/", GenericTaskCreateView.as_view()),
    path("update-task/<pk>", GenericTaskUpdateView.as_view()),
    path("detail-task/<pk>", GenericTaskDetailView.as_view()),
    path("delete-task/<pk>", GenericTaskDeleteView.as_view()),
    # path("complete-task/<pk>", GenericTaskCompleteView.as_view()),
    # path("completed-tasks/", GenericCompletedTaskView.as_view()),
    # path("all-tasks/", GenericAllTaskView.as_view()),
    # path("sessiontest/", session_storage_view),
    path("user/signup/", UserCreateView.as_view()),
    path("user/login/", UserLoginView.as_view()),
    path("user/logout/", LogoutView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += staticfiles_urlpatterns()
