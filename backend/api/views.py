from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm, ClienteCreationForm, FundacionCreationForm

def hola(request):
    return render(request, 'hola.html')

def registro(request):
    return render(request, 'registro.html')

def register_cliente(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirige a la página de inicio u otra página
    else:
        form = ClienteCreationForm()
    return render(request, 'registro_cliente.html', {'form': form})

def register_fundacion(request):
    if request.method == 'POST':
        form = FundacionCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirige a la página de inicio u otra página
    else:
        form = FundacionCreationForm()
    return render(request, 'registro_fundacion.html', {'form': form})