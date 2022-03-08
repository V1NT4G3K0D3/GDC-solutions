from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.models import Task, TaskStatusChanges
from tasks.forms import UserCreationForm, UserLoginForm, TaskCreateForm
from django.shortcuts import render


def RootPage(request):
    return render(request, "root.html")


class AuthorisedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class UserLoginView(LoginView):
    template_name = "user/user_login.html"
    form_class = UserLoginForm


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user/user_create.html"
    success_url = "/user/login"


def session_storage_view(request):
    total_views = request.session.get("total_views", 0)
    request.session["total_views"] = total_views + 1
    return HttpResponse(
        f"""Total views is {total_views} and the user is {request.user} 
        and is authenticated : {request.user.is_authenticated}"""
    )


def push_data(priority, task_obj):
    update_tasks = []
    while True:
        task = Task.objects.filter(
            priority=priority,
            user=task_obj.user,
            deleted=False,
            completed=False,
        ).first()

        if task:
            task_obj.priority = priority
            update_tasks.append(task_obj)
            task_obj = task
            priority += 1
        else:
            task_obj.priority = priority
            update_tasks.append(task_obj)
            break
    Task.objects.bulk_update_or_create(
        update_tasks, ["priority"], match_field=["id"]
    )


class GenericTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "crud/task_delete.html"
    success_url = "/form-tasks"

    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.deleted = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = "crud/task_detail.html"


class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "crud/task_update.html"
    success_url = "/form-tasks"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user

        if form.has_changed():
            if "status" in form.changed_data:
                task_status = TaskStatusChanges(
                    task=self.object,
                    status=self.object.status,
                )
                task_status.save()

                if self.object.status == "COMPLETED":
                    self.object.completed = True
                else:
                    self.object.completed = False

            if "priority" in form.changed_data:
                push_data(self.object.priority, self.object)

            self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class GenericTaskCompleteView(AuthorisedTaskManager, UpdateView):
    model = Task
    fields = ["completed"]
    template_name = "crud/task_complete.html"
    success_url = "/form-all-tasks"


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = "crud/task_create.html"
    success_url = "/form-tasks"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        priority = self.object.priority
        self.object.user = self.request.user

        if "status" in form.changed_data:
            task_status = TaskStatusChanges(
                task=self.object,
                status=self.object.status,
            )
            task_status.save()

            if self.object.status == "COMPLETED":
                self.object.completed = True
            else:
                self.object.completed = False

        push_data(priority, self.object)
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskView(LoginRequiredMixin, ListView):
    template_name = "lists/tasks_pending.html"
    context_object_name = "pending_tasks"
    paginate_by = 5

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        tasks = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        ).order_by("priority")
        if search_item:
            tasks = tasks.filter(title__icontains=search_item)
        return tasks

    def get_context_data(self, **kwargs):
        context = super(GenericTaskView, self).get_context_data(**kwargs)
        context["user"] = self.request.user
        context["pending_count"] = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        ).count()
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        ...
        return context


class GenericCompletedTaskView(LoginRequiredMixin, ListView):
    template_name = "lists/tasks_completed.html"
    context_object_name = "completed_tasks"

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        tasks = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).order_by("priority")
        if search_item:
            tasks = tasks.filter(title__icontains=search_item)
        return tasks

    def get_context_data(self, **kwargs):
        context = super(GenericCompletedTaskView, self).get_context_data(
            **kwargs
        )
        context["user"] = self.request.user
        context["pending_count"] = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        ).count()
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        ...
        return context


class GenericAllTaskView(LoginRequiredMixin, ListView):
    template_name = "tasks_home.html"
    context_object_name = "tasks"

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        tasks = Task.objects.filter(user=self.request.user).order_by(
            "priority"
        )
        if search_item:
            tasks = tasks.filter(title__icontains=search_item)
        return tasks

    def get_context_data(self, **kwargs):
        context = super(GenericAllTaskView, self).get_context_data(**kwargs)
        context["user"] = self.request.user
        context["pending_count"] = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        ).count()
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        ...
        return context


class GenericDeletedTaskView(LoginRequiredMixin, ListView):
    template_name = "lists/tasks_deleted.html"
    context_object_name = "deleted_tasks"

    def get_queryset(self):
        search_item = self.request.GET.get("search")
        tasks = Task.objects.filter(
            deleted=True, user=self.request.user
        ).order_by("priority")
        if search_item:
            tasks = tasks.filter(title__icontains=search_item)
        return tasks

    def get_context_data(self, **kwargs):
        context = super(GenericDeletedTaskView, self).get_context_data(
            **kwargs
        )
        context["user"] = self.request.user
        context["pending_count"] = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        ).count()
        context["completed_count"] = Task.objects.filter(
            deleted=False, completed=True, user=self.request.user
        ).count()
        ...
        return context
