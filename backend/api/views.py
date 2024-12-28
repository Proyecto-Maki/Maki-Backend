from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import UserSerializer, ClienteSignupSerializer, FundacionSignupSerializer
from rest_framework.views import APIView
from .permissions import IsClienteUser, IsFundacionUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
# from .forms import RegistroForm, ClienteCreationForm, FundacionCreationForm
from .models import User, Cliente, Fundacion, OneTimePassword
from .utils import send_code_to_user

def hola(request):
    return render(request, 'hola.html')

class ClienteSignupView(generics.ListCreateAPIView):
    # serializer_class = ClienteSignupSerializer
    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     return Response({
    #             "user": UserSerializer(user, context=self.get_serializer_context()).data,
    #             "token": Token.objects.get(user=user).key,
    #             "message": "Cliente creado exitosamente",
    #         })
    queryset = Cliente.objects.all()
    serializer_class = ClienteSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_code_to_user(user.email)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "message": "Cliente creado exitosamente",
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class FundacionSignupView(generics.ListCreateAPIView):

    queryset = Fundacion.objects.all()
    serializer_class = FundacionSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "message": "Fundacion creada exitosamente",
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # serializer_class = FundacionSignupSerializer
    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     return Response({
    #             "user": UserSerializer(user, context=self.get_serializer_context()).data,
    #             "token": Token.objects.get(user=user).key,
    #             "message": "Fundacion creada exitosamente",
    #         })


# class CustomAuthToken(ObtainAuthToken):
#     serializer_class = EmailAuthSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data, context={'request':request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.pk,
#             'is_cliente': user.is_cliente,
#             'is_fundacion': user.is_fundacion,
#         })

class VerificarCodigo(generics.GenericAPIView):
    def post(self, request):
        otpcode = request.data.get('otp')   
        try:
            user_code_obj = OneTimePassword.objects.get(code=otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': 'Usuario verificado exitosamente'
                }, status=status.HTTP_200_OK)
            return Response({
                'message': 'Código no es válido. Usuario ya verificado'
            }, status=status.HTTP_204_NO_CONTENT)
        
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'Código no es válido'
            }, status=status.HTTP_404_NOT_FOUND)
class CustomAuthToken(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        credentials ={
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }

        user  = authenticate(**credentials)
        if user:
            if not user.is_active:
                raise exceptions.AuthenticationFailed('User account is disabled.')
            if not user.is_verified:
                raise exceptions.AuthenticationFailed('User account is not verified.')
            data = {}
            refresh = self.get_token(user)
            data['email'] = user.email
            data['is_cliente'] = user.is_cliente
            data['is_fundacion'] = user.is_fundacion
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
          
            return data
        else:
            raise exceptions.AuthenticationFailed('Unable to log in with provided credentials.')
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomAuthToken

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