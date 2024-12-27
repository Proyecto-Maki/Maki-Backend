from django.shortcuts import render, redirect
from django.contrib.auth import login
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, ClienteSignupSerializer, FundacionSignupSerializer
# from .forms import RegistroForm, ClienteCreationForm, FundacionCreationForm

def hola(request):
    return render(request, 'hola.html')

class ClienteSignupView(generics.CreateAPIView):
    serializer_class = ClienteSignupSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": Token.objects.get(user=user).key,
                "message": "Cliente creado exitosamente",
            })
    
class FundacionSignupView(generics.CreateAPIView):
    serializer_class = FundacionSignupSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": Token.objects.get(user=user).key,
                "message": "Fundacion creada exitosamente",
            })



# def registro(request):
#     return render(request, 'registro.html')

# def register_cliente(request):
#     if request.method == 'POST':
#         form = ClienteCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')  # Redirige a la página de inicio u otra página
#     else:
#         form = ClienteCreationForm()
#     return render(request, 'registro_cliente.html', {'form': form})

# def register_fundacion(request):
#     if request.method == 'POST':
#         form = FundacionCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')  # Redirige a la página de inicio u otra página
#     else:
#         form = FundacionCreationForm()
#     return render(request, 'registro_fundacion.html', {'form': form})