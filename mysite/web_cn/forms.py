from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    group_choices = [
        ('化學實驗室', '化學實驗室'),
        ('表面分析實驗室', '表面分析實驗室'),
        ('成分分析實驗室', '成分分析實驗室'),
        ('Fab A', 'Fab A'),
        ('Fab B', 'Fab B'),
        ('Fab C', 'Fab C'),
    ]
    group = forms.ChoiceField(choices=group_choices)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            group_name = self.cleaned_data['group']
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        return user