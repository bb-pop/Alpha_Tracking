from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'name', 'phone_number', 'photo_profile', 'role')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'phone_number', 'photo_profile', 'role')


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    number = forms.CharField(max_length=15)
    faceimage = forms.CharField(widget=forms.HiddenInput())
