from django import forms
from .models import User, Action, Task, Pensee_Bete, link


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'date_of_birth', 'profile_picture', 'role', 'is_active'
        ]

class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ['user', 'action_title', 'description']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status']

class PenseeBeteForm(forms.ModelForm):
    class Meta:
        model = Pensee_Bete
        fields = ['user', 'content']

class LinkForm(forms.ModelForm):
    class Meta:
        model = link
        fields = ['user', 'url', 'description']