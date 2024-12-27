from django import forms
from django.contrib.auth.forms import UserCreationForm
# from .models import Cliente, Fundacion

# class RegistroForm(forms.Form):
#     nombre = forms.CharField(max_length=100)
#     email = forms.EmailField()
#     contraseña = forms.CharField(widget=forms.PasswordInput())

# class ClienteCreationForm(UserCreationForm):
#     class Meta:
#         model = Cliente
#         fields = ('username', 'direccion', 'telefono', 'saldo', 'password1', 'password2')

# class FundacionCreationForm(UserCreationForm):
#     class Meta:
#         model = Fundacion
#         fields = ('username', 'direccion', 'telefono', 'saldo', 'password1', 'password2')