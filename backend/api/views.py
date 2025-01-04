from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import *
from rest_framework.views import APIView
from .permissions import IsClienteUser, IsFundacionUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
# from .forms import RegistroForm, ClienteCreationForm, FundacionCreationForm
from .models import *
# from .utils import send_code_to_user
from .new_utils import send_code_to_user, send_test_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view


@api_view(['GET'])
def SendTestEmail(request):
    try: 
        response = send_test_email()
        return Response({response['message']})
    except Exception as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

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
                "message": "Cliente creado exitosamente. Se envió un código de verificación a tu correo electrónico",
            }, status=status.HTTP_201_CREATED)
        
        errores = {}
        for key, value in serializer.errors.items():
            errores[key] = ", ".join(value)

        mensaje = " | ".join([f"{key}: {value}" for key, value in errores.items()])
        return Response({
            "error": serializer.errors,
            "message": mensaje,
            }, status=status.HTTP_400_BAD_REQUEST)

    
class FundacionSignupView(generics.ListCreateAPIView):

    queryset = Fundacion.objects.all()
    serializer_class = FundacionSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_code_to_user(user.email)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "message": "Fundacion creada exitosamente. Se envió un código de verificación a tu correo electrónico",
            }, status=status.HTTP_201_CREATED)
        errores = {}
        for key, value in serializer.errors.items():
            errores[key] = ", ".join(value)

        mensaje = " | ".join([f"{key}: {value}" for key, value in errores.items()])
        return Response({
            "error": serializer.errors,
            "message": mensaje,
            }, status=status.HTTP_400_BAD_REQUEST)
    

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
                raise exceptions.AuthenticationFailed('La cuenta no está activa.')
            if not user.is_verified:
                raise exceptions.AuthenticationFailed('La cuenta no está verificada.')
                
            data = {}
            refresh = self.get_token(user)
            data['email'] = user.email
            data['is_cliente'] = user.is_cliente
            data['is_fundacion'] = user.is_fundacion
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
          
            return {'data': data, 'message': '¡Bienvenido a Maki!'}
        else:
            raise exceptions.AuthenticationFailed('No es posible iniciar sesión con esas credenciales.')
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomAuthToken

class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
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
    
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Se envió a tu correo electrónico un link para restablecer tu contraseña'}, status=status.HTTP_200_OK)

class PasswordResetConfirm(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message': 'Token no es válido o está expirado'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Credenciales válidas', 'uidb6':uidb64, 'token':token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
            return Response(
                {'message': 'Token no es válido o está expirado'}, 
                status=status.HTTP_401_UNAUTHORIZED)

class SetNewPassword(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Contraseña restablecida exitosamente'}, status=status.HTTP_200_OK)
        # serializer.is_valid(raise_exception=True)
        return Response({
            'error': serializer.errors,
            'message': 'Ha ocurrido un error para restablecer la contraseña'}, 
            status=status.HTTP_400_BAD_REQUEST)



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


### METODOS DE GETS, PUTS y DELETES


class CurrentUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'email': user.email, 'is_cliente': user.is_cliente, 'is_fundacion': user.is_fundacion})
    

class ClienteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()

    def get_object(self):
        email = self.request.query_params.get('email')
        if not email:
            raise ValueError("Debes proporcionar un parámetro 'email' en la consulta.")
        
        # Busca el usuario con el email proporcionado
        user = get_object_or_404(User, email=email)

        # Busca el cliente asociado al usuario encontrado
        cliente = get_object_or_404(self.queryset, user=user)

        return cliente
    
class FundacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = FundacionSerializer
    queryset = Fundacion.objects.all()

    def get_object(self):
        email = self.request.query_params.get('email')
        if not email:
            raise ValueError("Debes proporcionar un parámetro 'email' en la consulta.")
        
        user = get_object_or_404(User, email=email)

        fundacion = get_object_or_404(self.queryset, user=user)

        return fundacion
    

class MascotaCreateView(generics.ListCreateAPIView):
    queryset = Mascota.objects.all()
    permissions_classes = [permissions.AllowAny]
    serializer_class = MascotaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Mascota creada exitosamente'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'error': serializer.errors,
            'message': 'Ha ocurrido un error al crear la mascota'
        }, status=status.HTTP_400_BAD_REQUEST)

class MascotasUserView(generics.ListAPIView):
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        email = self.kwargs.get('email')
        user = get_object_or_404(User, email=email)
        return Mascota.objects.filter(user=user)
    

# class ProductosView(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Producto.objects.all()
#     serializer_class = ProductoSerializer
