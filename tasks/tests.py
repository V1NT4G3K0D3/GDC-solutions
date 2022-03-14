from django.test import TestCase
from tasks.models import STATUS_CHOICES, Task, User, Preference
from tasks.forms import TaskCreateForm, UserCreationForm, MailPreferenceForm
from tasks.tasks import send_email_reminder, app
from django.utils import timezone
from django.test import TransactionTestCase
from django.core import mail
from celery.contrib.testing.worker import start_worker
from unittest.mock import patch


class ModelTests(TestCase):
    def setUp(self):
        self.usernames = [
            "user1",
            "user2",
            "admin",
        ]
        self.password = "happyuser1234"
        self.task = {
            "title": "Dummy task",
            "description": "Dummy description",
            "priority": 1,
        }

    def login(self, username, password):
        response = self.client.post(
            "/user/login/", {"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/tasks")

    def logout(self):
        response = self.client.get("/user/logout/")
        self.assertEqual(response.url, "/")
        self.assertEqual(response.status_code, 302)

    def add_task(self, **kwargs):
        return self.client.post(
            "/form-create-task/",
            {
                "title": kwargs["title"],
                "description": "Description",
                "completed": kwargs.get("completed") or False,
                "deleted": kwargs.get("deleted") or False,
                "status": STATUS_CHOICES[0][1],
                "priority": kwargs.get("priority") or 1,
            },
        )

    def update_task(self, **kwargs):
        task = Task.objects.get(pk=kwargs["pk"])
        return self.client.post(
            f"/update-task/{task.pk}/",
            {
                "title": kwargs.get("title") or task.title,
                "description": kwargs.get("description") or task.description,
                "completed": kwargs.get("completed") or task.completed,
                "deleted": kwargs.get("deleted") or task.completed,
                "status": kwargs.get("status") or task.status,
                "priority": kwargs.get("priority") or task.priority,
            },
        )

    def delete_task(self, **kwargs):
        task: Task = Task.objects.get(pk=kwargs.get("pk"))
        return self.client.post(f"/delete-task/{task.pk}/")


class UserModelTests(ModelTests):
    def test_authenticated(self):
        """
        Try to GET the tasks listing page, expect the response to redirect to the login page
        """
        response = self.client.get("/form-tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/form-tasks/")

    def test_authenticated_with_user(self):
        for username in self.usernames:

            self.assertFalse(User.objects.filter(username=username).exists())

            response = self.client.post(
                "/user/signup/",
                {
                    "username": username,
                    "password1": self.password,
                    "password2": self.password,
                },
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, f"/user/login")

            self.assertTrue(User.objects.filter(username=username).exists())

            response = self.client.post(
                "/user/login/", {"username": username, "password": self.password}
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/tasks")

        self.assertEqual(User.objects.all().count(), 3)


class FormTests(ModelTests):
    def test_create_user_form(self):
        form = TaskCreateForm(
            data={
                "title": "A",
                "description": "New task",
                "priority": 1,
                "status": STATUS_CHOICES[0][0],
            }
        )

        self.assertEqual(form.errors["title"], ["Data too small"])

    def test_mail_preference_form(self):
        form = MailPreferenceForm(data={"preferred_time": "2022-02-15 07:25:00+00:00"})
        self.assertTrue(form.is_valid())

    def test_user_creation_form(self):
        form = UserCreationForm(
            data={
                "username": self.usernames[0],
                "password1": self.password,
                "password2": self.password,
            }
        )
        self.assertTrue(form.is_valid())


class FormTaskModelTests(UserModelTests, ModelTests):
    def test_create_task(self):
        self.test_authenticated_with_user()
        self.assertEqual(User.objects.all().count(), 3)
        for user in User.objects.all():
            self.login(user.username, self.password)

            for title in ["Task 1", "Task 2", "Task 3"]:
                response = self.add_task(title=title)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, "/form-tasks")

            response = self.client.get("/form-tasks/")
            self.assertEqual(
                set(response.context["tasks"]),
                set(Task.objects.filter(user=user, completed=False, deleted=False)),
            )

            self.logout()


class MailTasks(
    ModelTests,
    TransactionTestCase,
):
    def test_send_mail(self):
        user = User.objects.create(
            username="user", password=self.password, email="user@mail.com"
        )
        user.preference.preferred_time = timezone.now() + timezone.timedelta(days=1)
        user.save()
        user.preference.save()
        send_email_reminder()
        self.assertEqual(len(mail.outbox), 1)
