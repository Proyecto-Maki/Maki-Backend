from django.shortcuts import render, redirect
from django.contrib.auth import login
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer, ClienteSignupSerializer, FundacionSignupSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from .permissions import IsClienteUser, IsFundacionUser
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


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'is_cliente': user.is_cliente,
            'is_fundacion': user.is_fundacion,
        })
    
class LogoutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)
    
class ClienteOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated&IsClienteUser]
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

class FundacionOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated&IsFundacionUser]
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user
    

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