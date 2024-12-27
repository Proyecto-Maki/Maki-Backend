from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente

class RegistroForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    contraseña = forms.CharField(widget=forms.PasswordInput())