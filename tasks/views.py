from django.http import HttpResponseRedirect
from django.shortcuts import render

from tasks.models import Task


def tasks_view(request):
    search_item = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False, completed=False)

    if search_item:
        tasks = tasks.filter(title__icontains=search_item)

    return render(request, "tasks.html", {"tasks": tasks})


def add_tasks_view(request):
    task_val = request.GET.get("task")
    Task(title=task_val).save()
    return HttpResponseRedirect("/tasks")


def delete_tasks_view(request, id):
    Task.objects.filter(id=id).update(deleted=True)
    return HttpResponseRedirect("/tasks")


def complete_task_view(request, id):
    Task.objects.filter(id=id).update(completed=True)
    return HttpResponseRedirect("/completed_tasks")


def completed_tasks_view(request):
    completed_tasks = Task.objects.filter(deleted=False, completed=True)
    return render(request, "completed_tasks.html", {"completed_tasks": completed_tasks})


def all_tasks_view(request):
    pending_tasks = Task.objects.filter(deleted=False, completed=False)
    completed_tasks = Task.objects.filter(deleted=False, completed=True)
    return render(
        request,
        "all_tasks.html",
        {"pending_tasks": pending_tasks, "completed_tasks": completed_tasks},
    )
