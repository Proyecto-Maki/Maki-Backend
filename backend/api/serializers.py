from rest_framework import serializers
from .models import User, Cliente, Fundacion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_cliente', 'direccion', 'telefono']

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
        fields = ['username', 'email', 'password', 'password2', 'direccion', 'telefono', 'primer_nombre', 'primer_apellido', 'segundo_nombre', 'segundo_apellido']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        user = User(
            username=self.validated_data['username'],
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
        fields = ['username', 'email', 'password', 'password2', 'direccion', 'telefono','nombre', 'nit', 'descripcion']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        user = User(
            username=self.validated_data['username'],
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