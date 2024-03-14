from django import forms

from django.contrib.auth.models import User
from proj.models import Student, Task

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', "email", "password", "first_name", "last_name")

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("branch", "section", "year_of_joining")


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ("name", "description", "schedule_after", "deadline", "duration", "is_important", "is_fixed", "has_intrest")
        widgets = {
            "deadline": forms.DateTimeInput(attrs={'type':'datetime-local'}),
            "schedule_after": forms.DateTimeInput(attrs={'type':'datetime-local'}),
        }

