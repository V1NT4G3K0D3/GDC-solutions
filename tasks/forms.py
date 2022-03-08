from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, ValidationError
from django.contrib.auth.forms import UserCreationForm
from tasks.models import Task, User


class SetInitForForms:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_input = """mt-1 mb-2 px-3 py-3 bg-white border 
                shadow-sm border-slate-300 placeholder-slate-400 
                focus:outline-none focus:border-sky-500 focus:ring-sky-500 
                block w-full rounded-lg sm:text-sm focus:ring-1 bg-gray-200"""

        for index, visible in enumerate(self.visible_fields()):
            # print(visible.field.help_text)
            visible.field.widget.attrs["class"] = class_input


class UserCreationForm(SetInitForForms, UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
        help_texts = {
            "username": "150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        }


class UserLoginForm(SetInitForForms, AuthenticationForm):
    pass


class TaskCreateForm(SetInitForForms, ModelForm):
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Data too small")
        return title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible_fields()[3].field.widget.attrs[
            "class"
        ] = """mb-6 form-check-input h-4 w-4 
        border border-gray-100 rounded-sm bg-white 
        checked:bg-blue-600 checked:border-blue-600 
        focus:outline-none transition duration-200 mt-1 align-top 
        cursor-pointer"""

    class Meta:
        model = Task
        fields = ["title", "description", "priority", "completed", "status"]
