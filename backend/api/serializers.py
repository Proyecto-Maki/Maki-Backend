from rest_framework import serializers
from .models import User, Cliente, Fundacion
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_str, smart_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import send_normal_email
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','is_cliente', 'direccion', 'telefono','saldo']

class ClienteSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    direccion = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True, write_only=True)
    primer_nombre = serializers.CharField(max_length=255, required=True, allow_blank=True, write_only=True)
    primer_apellido = serializers.CharField(max_length=255, required=True, allow_blank=True, write_only=True)
    segundo_nombre = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    segundo_apellido = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'direccion', 'telefono', 'primer_nombre', 'primer_apellido', 'segundo_nombre', 'segundo_apellido']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        direccion = self.validated_data.get('direccion', '')
        telefono = self.validated_data.get('telefono', '')

        if password != password2:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden'})
        user.set_password(password)
        user.direccion = direccion
        user.telefono = telefono
        user.is_cliente = True
        user.save()

        primer_nombre = self.validated_data.get('primer_nombre', '')
        primer_apellido = self.validated_data.get('primer_apellido', '')
        segundo_nombre = self.validated_data.get('segundo_nombre', '')
        segundo_apellido = self.validated_data.get('segundo_apellido', '')

        Cliente.objects.create(
            user=user,
            primer_nombre=primer_nombre,
            primer_apellido=primer_apellido,
            segundo_nombre=segundo_nombre,
            segundo_apellido=segundo_apellido,
        )
        return user

class FundacionSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    direccion = serializers.CharField(max_length=255, required=False, allow_blank=True, write_only=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True, write_only=True)
    nombre = serializers.CharField(max_length=255, required=True, allow_blank=True, write_only=True)
    nit = serializers.CharField(max_length=255, required=True, allow_blank=True, write_only=True)
    descripcion = serializers.CharField(max_length=255, required=True, allow_blank=True, write_only=True)
    # premium = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'direccion', 'telefono','nombre', 'nit', 'descripcion']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        direccion = self.validated_data.get('direccion', '')
        telefono = self.validated_data.get('telefono', '')

        if password != password2:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden'})
        user.set_password(password)
        user.direccion = direccion
        user.telefono = telefono
        user.is_fundacion = True
        user.save()

        nombre = self.validated_data.get('nombre', '')
        nit = self.validated_data.get('nit', '')
        descripcion = self.validated_data.get('descripcion', '')
        # premium = self.validated_data.get('premium', False)
        Fundacion.objects.create(
            user=user,
            nombre=nombre,
            nit=nit,
            descripcion=descripcion
        )
        return user
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True, allow_blank=False)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            site_domain = get_current_site(request).domain
            relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            abslink = f"http://{site_domain}{relative_link}"
            email_body = f"¡Hola! Usa el siguiente enlace para restablecer tu contraseña: \n {abslink}"
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Restablecer contraseña'
            }

            send_normal_email(data)
        return super().validate(attrs)


# class EmailAuthSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

#     def validate(self, attrs):
#         email = attrs.get('email')
#         password = attrs.get('password')

#         if email and password:
#             user = authenticate(request=self.context.get('request'), username=email, password=password)
#             if not user:
#                 msg = 'Unable to log in with provided credentials.'
#                 raise serializers.ValidationError(msg, code='authorization')
#         else:
#             msg = 'Must include "email" and "password".'
#             raise serializers.ValidationError(msg, code='authorization')

#         attrs['user'] = user
#         return attrs