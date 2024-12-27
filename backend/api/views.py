from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm

def hola(request):
    return render(request, 'hola.html')

def registro(request):
    return render(request, 'registro.html')