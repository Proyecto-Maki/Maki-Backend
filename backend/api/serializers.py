from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.exceptions import AuthenticationFailed
from django.urls import reverse
from datetime import date

# from .utils import send_normal_email
from .new_utils import send_normal_email
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class LocalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localidad
        fields = ["id", "nombre"]

class DireccionSerializer(serializers.ModelSerializer):
    direccion = serializers.CharField(max_length=255)
    codigo_postal = serializers.CharField(max_length=6, required=False, allow_blank=True)
    id_localidad = serializers.IntegerField()

    class Meta:
        model = Direccion
        fields = ["id", "direccion", "codigo_postal", "id_localidad"]

    def save(self, **kwargs):
        direccion = self.validated_data["direccion"]
        codigo_postal = self.validated_data.get("codigo_postal", "")
        id_localidad = self.validated_data["id_localidad"]

        localidad = Localidad.objects.get(id=id_localidad)
        direccion = Direccion.objects.create(
            direccion=direccion, codigo_postal=codigo_postal, localidad=localidad
        )
        return direccion
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "is_cliente",
            "direccion",
            "telefono",
            "saldo",
            "is_verified",
        ]


class ClienteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    direccion = serializers.CharField(source="user.direccion.direccion")
    codigo_postal = serializers.CharField(source="user.direccion.codigo_postal")
    localidad = serializers.CharField(source="user.direccion.localidad.nombre")
    telefono = serializers.CharField(source="user.telefono")
    saldo = serializers.DecimalField(
        source="user.saldo", max_digits=7, decimal_places=2
    )
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)

    class Meta:
        model = Cliente
        fields = [
            "email",
            "direccion",
            "codigo_postal",
            "localidad",
            "telefono",
            "saldo",
            "is_verified",
            "cedula",
            "primer_nombre",
            "primer_apellido",
            "segundo_nombre",
            "segundo_apellido",
            "fecha_nacimiento",
        ]

    def update(self, instance_cliente, validated_data):
        user_data = validated_data.pop("user", {})

        instance_user = instance_cliente.user
        for attr, value in user_data.items():
            setattr(instance_user, attr, value)
        instance_user.save()

        for attr, value in validated_data.items():
            setattr(instance_cliente, attr, value)
        instance_cliente.save()

        return instance_cliente


class FundacionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    direccion = serializers.CharField(source="user.direccion.direccion")
    codigo_postal = serializers.CharField(source="user.direccion.codigo_postal")
    localidad = serializers.CharField(source="user.direccion.localidad.nombre")
    telefono = serializers.CharField(source="user.telefono", read_only=True)
    saldo = serializers.DecimalField(
        source="user.saldo", max_digits=7, decimal_places=2, read_only=True
    )
    is_verified = serializers.BooleanField(source="user.is_verified", read_only=True)

    class Meta:
        model = Fundacion
        fields = [
            "email",
            "direccion",
            "codigo_postal",
            "localidad",
            "telefono",
            "saldo",
            "is_verified",
            "nombre",
            "nit",
            "descripcion",
        ]

    def update(self, instance_fundacion, validated_data):
        user_data = validated_data.pop("user", {})

        instance_user = instance_fundacion.user
        for attr, value in user_data.items():
            setattr(instance_user, attr, value)
        instance_user.save()

        for attr, value in validated_data.items():
            setattr(instance_fundacion, attr, value)
        instance_fundacion.save()
        return instance_fundacion


class ClienteSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    direccion = serializers.CharField(max_length=255, required=True, allow_blank=True)
    codigo_postal = serializers.CharField(
        max_length=6, required=False, allow_blank=True, write_only=True
    )
    id_localidad = serializers.IntegerField(write_only=True)
    telefono = serializers.CharField(
        max_length=10, required=False, allow_blank=True, write_only=True
    )
    primer_nombre = serializers.CharField(
        max_length=255, required=True, allow_blank=True, write_only=True
    )
    primer_apellido = serializers.CharField(
        max_length=255, required=True, allow_blank=True, write_only=True
    )
    segundo_nombre = serializers.CharField(
        max_length=255, required=False, allow_blank=True, write_only=True
    )
    cedula = serializers.CharField(
        max_length=10, required=True, allow_blank=True, write_only=True
    )
    segundo_apellido = serializers.CharField(
        max_length=255, required=False, allow_blank=True, write_only=True
    )

    fecha_nacimiento = serializers.DateField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "direccion",
            "codigo_postal",
            "id_localidad",
            "telefono",
            "cedula",
            "primer_nombre",
            "primer_apellido",
            "segundo_nombre",
            "segundo_apellido",
            "fecha_nacimiento",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_fecha_nacimiento(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError({
                "detail": "Debes ser mayor de edad para registrarte"
            })
        return value

    def save(self, **kwargs):
        user = User(
            email=self.validated_data["email"],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]
        direccion_dir = self.validated_data.get("direccion", "")
        codigo_postal = self.validated_data.get("codigo_postal", "")
        id_localidad = self.validated_data.get("id_localidad", "")
        telefono = self.validated_data.get("telefono", "")

        direccion = Direccion.objects.create(
            direccion = direccion_dir,
            codigo_postal = codigo_postal,
            localidad = Localidad.objects.get(id=id_localidad)
        )

        if password != password2:
            raise serializers.ValidationError(
                {"detail": "Las contraseñas no coinciden"}
            )
        user.set_password(password)
        user.direccion = direccion
        user.telefono = telefono

        user.is_cliente = True
        user.is_verified = False  # Set is_verified to False
        user.save()
        cedula = self.validated_data.get("cedula", "")
        primer_nombre = self.validated_data.get("primer_nombre", "")
        primer_apellido = self.validated_data.get("primer_apellido", "")
        segundo_nombre = self.validated_data.get("segundo_nombre", "")
        segundo_apellido = self.validated_data.get("segundo_apellido", "")
        fecha_nacimiento = self.validated_data.get("fecha_nacimiento", None)
        self.validate_fecha_nacimiento(fecha_nacimiento)
        

        Cliente.objects.create(
            user=user,
            cedula=cedula,
            primer_nombre=primer_nombre,
            primer_apellido=primer_apellido,
            segundo_nombre=segundo_nombre,
            segundo_apellido=segundo_apellido,
            fecha_nacimiento=fecha_nacimiento
        )
        return user


class FundacionSignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    direccion = serializers.CharField(max_length=255, required=True, allow_blank=True)
    codigo_postal = serializers.CharField(
        max_length=6, required=False, allow_blank=True, write_only=True
    )
    id_localidad = serializers.IntegerField(write_only=True)
    telefono = serializers.CharField(
        max_length=10, required=False, allow_blank=True, write_only=True
    )
    nombre = serializers.CharField(
        max_length=255, required=True, allow_blank=True, write_only=True
    )
    nit = serializers.CharField(
        max_length=255, required=True, allow_blank=True, write_only=True
    )
    descripcion = serializers.CharField(
        max_length=500, required=True, allow_blank=True, write_only=True
    )
    # premium = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "direccion",
            "codigo_postal",
            "id_localidad",
            "telefono",
            "nombre",
            "nit",
            "descripcion",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def save(self, **kwargs):
        user = User(
            email=self.validated_data["email"],
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]
        direccion_dir = self.validated_data.get("direccion", "")
        codigo_postal = self.validated_data.get("codigo_postal", "")
        id_localidad = self.validated_data.get("id_localidad", "")

        direccion = Direccion.objects.create(
            direccion = direccion_dir,
            codigo_postal = codigo_postal,
            localidad = Localidad.objects.get(id=id_localidad)
        )
        telefono = self.validated_data.get("telefono", "")

        if password != password2:
            raise serializers.ValidationError(
                {"detail": "Las contraseñas no coinciden"}
            )
        user.set_password(password)
        user.direccion = direccion
        user.telefono = telefono
        user.is_fundacion = True
        user.is_verified = False  # Set is_verified to False
        user.save()

        nombre = self.validated_data.get("nombre", "")
        nit = self.validated_data.get("nit", "")
        descripcion = self.validated_data.get("descripcion", "")
        # premium = self.validated_data.get('premium', False)
        Fundacion.objects.create(
            user=user, nombre=nombre, nit=nit, descripcion=descripcion
        )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True, allow_blank=False)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get("request")
            # site_domain = get_current_site(request).domain
            # site_domain = "localhost:3000"
            site_domain = "https://www.makishop.live"
            relative_link = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            abslink = f"{site_domain}{relative_link}"
            # email_body = f"¡Hola! Usa el siguiente enlace para restablecer tu contraseña: \n {abslink}"
            data = {
                "email": email,
                "link": abslink,
                "to_email": user.email,
                "email_subject": "Restablecer contraseña",
            }

            send_normal_email(data)
        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=100, write_only=True)
    confirm_password = serializers.CharField(
        min_length=6, max_length=100, write_only=True
    )
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ["password", "confirm_password", "uidb64", "token"]

    def validate(self, attrs):

        try:
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")
            password = attrs.get("password")
            confirm_password = attrs.get("confirm_password")
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("El enlace no es válido o ha expirado", 401)

            if password != confirm_password:
                raise AuthenticationFailed("Las contraseñas no coinciden", 401)
            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            raise AuthenticationFailed("El enlace no es válido o ha expirado", 401)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {"bad_token": ("Token no es válido o ha expirado")}

    def validate(self, attrs):
        self.token = attrs.get("refresh_token")
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail("bad_token")


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


class MascotaSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=255, required=True, allow_blank=False, write_only=True
    )
    nombre = serializers.CharField(max_length=255, required=True, allow_blank=True)
    sexo = serializers.CharField(max_length=1, required=True, allow_blank=True)
    tipo = serializers.CharField(max_length=255, required=True, allow_blank=True)
    raza = serializers.CharField(max_length=255, required=True, allow_blank=True)
    edad = serializers.IntegerField(required=True)
    estado_salud = serializers.CharField(
        max_length=255, required=True, allow_blank=True
    )
    tamano = serializers.CharField(max_length=1, required=True, allow_blank=True)
    peso = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    imagen = serializers.ImageField(required=False)

    class Meta:
        model = Mascota
        fields = [
            "id",
            "email",
            "nombre",
            "sexo",
            "tipo",
            "raza",
            "edad",
            "estado_salud",
            "tamano",
            "peso",
            "imagen",
        ]

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        nombre = self.validated_data["nombre"]
        sexo = self.validated_data["sexo"]
        tipo = self.validated_data["tipo"]
        raza = self.validated_data["raza"]
        edad = self.validated_data["edad"]
        estado_salud = self.validated_data["estado_salud"]
        tamano = self.validated_data["tamano"]
        peso = self.validated_data["peso"]
        imagen = self.validated_data.get("imagen", None)
        mascota = Mascota.objects.create(
            user=user,
            nombre=nombre,
            sexo=sexo,
            tipo=tipo,
            raza=raza,
            edad=edad,
            estado_salud=estado_salud,
            tamano=tamano,
            peso=peso,
            imagen=imagen,
        )
        return mascota

    def update(self, instance, validated_data):
        """
        Actualiza los datos de la mascota si es necesario.
        Este método será invocado solo si el serializador es válido.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "slug",
            "imagen",
            "descripcion",
            "categoria",
            "precio",
            "ingredientes",
        ]


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = ["descripcion", "porcentaje"]


class CarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrito
        fields = ["id", "codigo", "creado", "modificado"]


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    carrito = CarritoSerializer(read_only=True)

    class Meta:
        model = ItemCarrito
        fields = ["id", "cantidad", "producto", "carrito"]


class PadecimientoSerializer(serializers.ModelSerializer):
    id_mascota = serializers.IntegerField(write_only=True)
    padecimiento = serializers.CharField(max_length=255)

    class Meta:
        model = Padecimiento
        fields = ["id", "id_mascota", "padecimiento"]

    def save(self, **kwargs):
        id_mascota = self.validated_data["id_mascota"]
        try:
            mascota = Mascota.objects.get(id=id_mascota)
        except Mascota.DoesNotExist:
            raise serializers.ValidationError({
                "detail": "La mascota no existe."
            })

        padecimiento = self.validated_data["padecimiento"]

        padecimiento_obj = Padecimiento.objects.create(
            mascota=mascota, padecimiento=padecimiento
        )
        return padecimiento_obj



class ResenaSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    id_producto = serializers.IntegerField(write_only=True)
    titulo = serializers.CharField(max_length=255)
    calificacion = serializers.IntegerField()
    comentario = serializers.CharField(max_length=500)

    class Meta:
        model = Resena
        fields = ["id", "email", "id_producto", "titulo", "calificacion", "comentario", "fecha"]

    def save(self, **kwargs):
        user = User.objects.get(email = self.validated_data["email"])
        producto = Producto.objects.get(id = self.validated_data["id_producto"])
        titulo = self.validated_data["titulo"]
        calificacion = self.validated_data["calificacion"]
        comentario = self.validated_data["comentario"]

        resena = Resena.objects.create(
            user=user,
            producto=producto,
            titulo=titulo,
            calificacion=calificacion,
            comentario=comentario
        )
        return resena
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()



### PEDIDOS

class PedidoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    estado = serializers.CharField(max_length=255)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    id_descuento = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Pedido
        fields = ["id", "email", "fecha", "estado", "id_descuento", "total"]

    def save(self, **kwargs):
        user = User.objects.get(email = self.validated_data["email"])
        total = self.validated_data["total"]
        estado = self.validated_data["estado"]
        id_descuento = self.validated_data["id_descuento"]

        if id_descuento:
            descuento = Descuento.objects.get(id = id_descuento)
            pedido = Pedido.objects.create(
                user = user,
                estado = estado,
                total = total,
                descuento = descuento
            )

            return pedido
        else:
            pedido = Pedido.objects.create(
                user = user,
                estado = estado,
                total = total
            )

        return pedido

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

class DetallePedidoSerializer(serializers.ModelSerializer):
    id_pedido = serializers.IntegerField(write_only=True)
    id_producto = serializers.IntegerField(write_only=True)
    cantidad = serializers.IntegerField()

    class Meta:
        model = DetallePedido
        fields = ["id", "id_pedido", "id_producto", "cantidad"]

    def save(self, **kwargs):
        id_pedido = self.validated_data["id_pedido"]
        id_producto = self.validated_data["id_producto"]
        cantidad = self.validated_data["cantidad"]

        pedido = Pedido.objects.get(id = id_pedido)
        producto = Producto.objects.get(id = id_producto)

        detalle = DetallePedido.objects.create(
            pedido = pedido,
            producto = producto,
            cantidad = cantidad
        )

        return detalle

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

class DetallePedidoConProductoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)

    class Meta:
        model = DetallePedido
        fields = ["id", "producto", "cantidad"]


class PublicacionAdopcionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    id_mascota = serializers.IntegerField(write_only=True)
    titulo = serializers.CharField(max_length=255)
    descripcion = serializers.CharField(max_length=500)
    direccion = serializers.CharField(max_length=255)
    id_localidad = serializers.IntegerField(write_only=True)
    mascota = MascotaSerializer(read_only=True)
    detalle_mascota = serializers.SerializerMethodField()

    class Meta:
        model = PublicacionAdopcion
        fields = ["id", "email", "id_mascota", "titulo", "descripcion", "direccion", "id_localidad", "fecha", "mascota", "detalle_mascota"]

    def get_detalle_mascota(self, obj):
        try:
            detalle_mascota = DetalleMascota.objects.get(mascota = obj.mascota) 
            return DetalleMascotaSerializer(detalle_mascota).data
        except DetalleMascota.DoesNotExist:
            return None

    def save(self, **kwargs):
        email = self.validated_data["email"]
        id_mascota = self.validated_data["id_mascota"]
        titulo = self.validated_data["titulo"]
        descripcion = self.validated_data["descripcion"]
        direccion_dir = self.validated_data["direccion"]
        id_localidad = self.validated_data["id_localidad"]

        user = User.objects.get(email = email)
        fundacion = Fundacion.objects.get(user = user)
        mascota = Mascota.objects.get(id = id_mascota)
        localidad = Localidad.objects.get(id = id_localidad)
        direccion = Direccion.objects.create(
            direccion = direccion_dir,
            localidad = localidad,
            codigo_postal = None
        )

        if PublicacionAdopcion.objects.filter(mascota=mascota).exists():
            raise serializers.ValidationError({
                "detail": "Ya existe una publicación con esta mascota.",
                "code": "duplicate_publication"
            })
        
        if not Mascota.objects.filter(id = id_mascota, user = user).exists():
            raise serializers.ValidationError({
                "detail": "No puedes publicar una mascota que no es tuya.",
                "code": "invalid_mascota"
            })

        publicacion = PublicacionAdopcion.objects.create(
            fundacion = fundacion,
            mascota = mascota,
            titulo = titulo,
            descripcion = descripcion,
            direccion = direccion
        )

        return publicacion
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

class DetalleMascotaSerializer(serializers.ModelSerializer):
    id_mascota = serializers.IntegerField(write_only=True)
    apto_ninos = serializers.BooleanField(required=True)
    espacio = serializers.CharField(max_length=255)
    apto_otras_mascotas = serializers.BooleanField(required=True)
    desparacitado = serializers.BooleanField(required=True)
    vacunado = serializers.BooleanField(required=True)
    esterilizado = serializers.BooleanField(required=True)


    class Meta: 
        model = DetalleMascota
        fields = ['id', 'id_mascota', 'apto_ninos', 'espacio', 'apto_otras_mascotas','desparacitado', 'vacunado', 'esterilizado']
    
    def save(self, **kwargs):
        id_mascota = self.validated_data["id_mascota"]
        apto_ninos = self.validated_data["apto_ninos"]
        espacio = self.validated_data["espacio"]
        apto_otras_mascotas = self.validated_data["apto_otras_mascotas"]
        desparacitado = self.validated_data["desparacitado"]
        vacunado = self.validated_data["vacunado"]
        esterilizado = self.validated_data["esterilizado"]

        mascota = Mascota.objects.get(id = id_mascota)

        if DetalleMascota.objects.filter(mascota = mascota).exists():
            raise serializers.ValidationError({
                "detail": "El detalle de la mascota ya existe",
            })
        
        detalle_mascota = DetalleMascota.objects.create(
            mascota = mascota,
            apto_ninos = apto_ninos,
            espacio = espacio,
            apto_otras_mascotas = apto_otras_mascotas,
            desparacitado = desparacitado,
            vacunado = vacunado,
            esterilizado = esterilizado
        )

        return detalle_mascota

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


## SOLICITUD DE ADOPCIÓN CLIENTES

class SolicitudAdopcionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    id_publicacion = serializers.IntegerField(write_only=True)
    motivo = serializers.CharField(max_length=500)

    class Meta: 
        model = SolicitudAdopcion
        fields = ['id', 'email', 'id_publicacion', 'motivo', 'fecha', 'estado']

    def save(self, **kwargs):
        email = self.validated_data["email"]
        id_publicacion = self.validated_data["id_publicacion"]

        cliente = Cliente.objects.get(user__email = email)
        publicacion = PublicacionAdopcion.objects.get(id = id_publicacion)

        if SolicitudAdopcion.objects.filter(cliente = cliente, publicacion = publicacion).exists():
            raise serializers.ValidationError({
                "detail": "Ya has solicitado esta adopción",
                "code": "duplicate_request"
            })
        
        motivo = self.validated_data["motivo"]

        solicitud_adopcion = SolicitudAdopcion.objects.create(
            cliente = cliente,
            publicacion = publicacion,
            motivo = motivo,
        )

        return solicitud_adopcion
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()



## CATEGORIAS

class CategoriaPrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPrincipal
        fields = ["id", "nombre"]

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "categoria_principal"]

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = ["id", "nombre", "categoria", "categoria_principal"]

class ProductoCategoriasSerializer(serializers.ModelSerializer):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sub_categoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)

    class Meta:
        model = ProductoCategorias
        fields = ["id", "producto", "sub_categoria"]



