# Add all your views here
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render

tasks = []
completed_tasks = []

def tasks_view(request):
    return render(request, "tasks.html", {"tasks": tasks})

def completed_tasks_view(request):
    return render(request, "completed_tasks.html", {"completed_tasks": completed_tasks})

def all_tasks_view(request):
    return render(request, "all_tasks.html", {"tasks": tasks, "completed_tasks": completed_tasks})
    
def add_tasks_view(request):
    task_val = request.GET.get("task")
    tasks.append(task_val)
    print(tasks)
    return HttpResponseRedirect("/tasks")

def delete_tasks_view(request, id):
    del tasks[id-1]
    return HttpResponseRedirect("/tasks")

def complete_task_view(request, id):
    completed_tasks.append(tasks[id-1])
    del tasks[id-1]
    return HttpResponseRedirect("/completed_tasks")

def remove_tasks_view(request, id):
    del completed_tasks[id-1]
    return HttpResponseRedirect("/tasks")