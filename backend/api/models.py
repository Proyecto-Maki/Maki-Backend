from django.conf import settings
from django.contrib.auth.models import (
    AbstractUser,
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Localidad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(nombre__gt=""),
                name="nombre_no_vacio",
            )
        ]

    def __str__(self):
        return f"{self.id} {self.nombre}"


class Direccion(models.Model):
    direccion = models.CharField(max_length=255, null=False, blank=False)
    codigo_postal = models.CharField(max_length=6, null=True, blank=True)
    localidad = models.ForeignKey(
        Localidad, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.direccion} {self.localidad.nombre}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # class Role(models.TextChoices):
    #     CLIENTE = 'CLIENTE', 'Cliente'
    #     FUNDACION = 'FUNDACION', 'Fundacion'
    #     ADMIN = 'ADMIN', 'Admin'

    # base_role = Role.ADMIN
    # role = models.CharField(max_length=50, choices=Role.choices)
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         self.role = self.base_role
    #         return super().save(*args, **kwargs)
    first_name = None
    last_name = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_cliente = models.BooleanField(default=False)
    is_fundacion = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    # username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    # direccion = models.CharField(max_length=255, null=True, blank=True)
    direccion = models.ForeignKey(
        Direccion, on_delete=models.CASCADE, null=True, blank=True
    )
    telefono = models.CharField(max_length=10, null=True, blank=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.BigIntegerField(unique=True, null=True, blank=True)
    primer_nombre = models.CharField(max_length=255, null=True, blank=True)
    segundo_nombre = models.CharField(max_length=255, null=True, blank=True)
    primer_apellido = models.CharField(max_length=255, null=True, blank=True)
    segundo_apellido = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # direccion = models.CharField(max_length=255, null=True, blank=True)
    # telefono = models.CharField(max_length=20, null=True, blank=True)
    # saldo = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"


class Fundacion(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    # direccion = models.CharField(max_length=255, null=True, blank=True)
    # telefono = models.CharField(max_length=20, null=True, blank=True)
    # saldo = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    nit = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    premium = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre}"


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"{self.user.email}-passcode"


def upload_to(instance, filename):
    return "images/{filename}".format(filename=filename)


# MODELO DE MASCOTA


class Mascota(models.Model):
    ESTADOS = {
        "Saludable": "Saludable",
        "Enfermo": "Enfermo",
        "Recuperacion": "Recuperacion",
    }
    SEXOS = {
        "M": "Macho",
        "H": "Hembra",
    }
    TAMANOS = {
        "P": "Pequeño",
        "M": "Mediano",
        "G": "Grande",
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False, blank=False)
    sexo = models.CharField(
        max_length=1, null=False, blank=False, choices=SEXOS, default="M"
    )
    tipo = models.CharField(max_length=255, null=False, blank=False)
    raza = models.CharField(max_length=255, null=False, blank=False)
    edad = models.IntegerField(null=False, blank=False)
    estado_salud = models.CharField(
        max_length=255, null=False, blank=False, choices=ESTADOS
    )
    tamano = models.CharField(max_length=1, null=False, blank=False, choices=TAMANOS)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=False)
    imagen = CloudinaryField("image", null=True, blank=True)

    def clean(self):
        if self.sexo not in self.SEXOS:
            raise ValidationError({"sexo": "Valor inválido para el campo sexo."})
        if self.estado_salud not in self.ESTADOS:
            raise ValidationError({"estado_salud": "Estado de salud inválido."})
        if self.tamano not in self.TAMANOS:
            raise ValidationError({"tamano": "Tamaño inválido."})

    def __str__(self):
        return f"{self.id} {self.nombre}"


## MODELO DE DETALLE DE MASCOTA - PARA PUBLICACION DE ADOPCION


class DetalleMascota(models.Model):

    ESPACIOS = {
        "P": "Pequeño",
        "G": "Grande",
    }
    mascota = models.OneToOneField(Mascota, on_delete=models.CASCADE)
    apto_ninos = models.BooleanField(default=False)
    apto_ruido = models.BooleanField(default=False)
    espacio = models.CharField(
        max_length=255, null=False, blank=False, choices=ESPACIOS
    )
    apto_otras_mascotas = models.BooleanField(default=False)
    desparasitado = models.BooleanField(default=False)
    vacunado = models.BooleanField(default=False)
    esterilizado = models.BooleanField(default=False)

    def __str__(self):
        return f"Detalles {self.mascota.nombre} - {self.mascota.tipo}"


## MODELO DE PADECIMIENTO


class Padecimiento(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    padecimiento = models.CharField(max_length=255, null=False, blank=False)

    def clean(self):
        if not self.padecimiento.strip():
            raise ValidationError({"padecimiento": "El campo no puede estar vacío."})

    def __str__(self):
        return f"{self.mascota.nombre} - {self.padecimiento}"


## MODELO DE PRODUCTO


class Producto(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    imagen = CloudinaryField("image", null=True, blank=True)
    descripcion = models.TextField(null=False, blank=False)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, null=False, blank=False
    )
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=255, null=False, blank=False)
    ingredientes = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generar el slug automáticamente si no está definido
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
        # super(Producto, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Carrito(models.Model):
    codigo = models.CharField(max_length=11, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    pagado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modificado = models.DateTimeField(auto_now=True, blank=True, null=True)

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError({"cantidad": "La cantidad no puede ser negativa."})

    def __str__(self):
        return self.codigo


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError({"cantidad": "La cantidad no puede ser negativa."})

    def __str__(self):
        return (
            f"{self.cantidad} x {self.producto.nombre} en carrito {self.carrito.codigo}"
        )


## MODELO DE PEDIDO


# Pendiente testing (cuando se implemente)
class Descuento(models.Model):
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, null=False, blank=False
    )

    def __str__(self):
        return f"{self.descripcion} - {self.porcentaje}%"


class Pedido(models.Model):

    ESTADOS = {
        "Preparación": "Preparación",
        "Entregado": "Entregado",
        "Transito": "Transito",
        "Cancelado": "Cancelado",
    }
    id = models.AutoField(primary_key=True)  # Lo pogo pa que abajo me deje poner el id
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    estado = models.CharField(
        max_length=255, null=False, blank=False, choices=ESTADOS, default="Preparación"
    )
    descuento = models.ForeignKey(
        Descuento, on_delete=models.SET_NULL, null=True, blank=True
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, null=False, blank=False
    )

    def clean(self):
        if self.estado not in self.ESTADOS.values():
            raise ValidationError({"estado": "El estado no es válido."})

    def __str__(self):
        return str(self.id)


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=False, blank=False)

    def clean(self):
        if self.cantidad < 0:
            raise ValidationError({"cantidad": "La cantidad no puede ser negativa."})

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"


## MODELO DE CUIDADOR


class Cuidador(models.Model):
    CATEGORIAS_MASCOTAS = {
        "Gatos": "Gatos",
        "Perros": "Perros",
        "Aves": "Aves",
        "Reptiles": "Reptiles",
        "Roedores": "Roedores",
        "Peces": "Peces",
    }
    primer_nombre = models.CharField(max_length=255, null=False, blank=False)
    segundo_nombre = models.CharField(max_length=255, null=True, blank=True)
    primer_apellido = models.CharField(max_length=255, null=False, blank=False)
    segundo_apellido = models.CharField(max_length=255, null=True, blank=True)
    cedula = models.BigIntegerField(unique=True, null=True, blank=True)
    imagen = CloudinaryField("imagen", null=True, blank=True)
    categoria_mascotas = models.CharField(
        max_length=8, null=True, blank=True, choices=CATEGORIAS_MASCOTAS
    )

    ocupacion = models.CharField(max_length=255, null=False, blank=False)
    localidad = models.ForeignKey(
        Localidad, on_delete=models.CASCADE, null=True, blank=True
    )
    experiencia = models.TextField(null=False, blank=False)
    hoja_vida = CloudinaryField("hoja_vida", null=True, blank=True)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

    telefono = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


## MODELO DE SOLICITUD DE CUIDADO


class SolicitudCuidado(models.Model):
    ESTADOS = {
        "Pendiente": "Pendiente",
        "Aceptada": "Aceptada",
        "Rechazada": "Rechazada",
        "Cancelada": "Cancelada",
        "Completada": "Completada",
    }

    id = models.AutoField(primary_key=True)  # Lo pongo pa que abajo me deje poner el id
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=False, blank=False)
    fecha_fin = models.DateTimeField(null=False, blank=False)
    horas_cuidado = models.IntegerField(null=False, blank=False, default=0)
    is_cuidado_especial = models.BooleanField(default=False)
    descripcion = models.TextField(null=False, blank=False)
    estado = models.CharField(
        max_length=255, null=False, blank=False, choices=ESTADOS, default="Pendiente"
    )
    costo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, null=False, blank=False
    )


## MODELO DE RESEÑA


class Resena(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    titulo = models.CharField(
        max_length=255, null=False, blank=False, default="Sin titulo"
    )
    calificacion = models.IntegerField(null=False, blank=False)
    comentario = models.TextField(null=True, blank=True)
    num_likes = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(calificacion__gte=1, calificacion__lte=5),
                name="calificacion_rango",
            )
        ]

    def __str__(self):
        return f"Reseña de {self.user.id}"


## MODELO DE DONACION


class Tarjeta(models.Model):
    tipo = models.CharField(max_length=255, null=False, blank=False, primary_key=True)
    monto = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00, null=False, blank=False
    )

    def clean(self):
        if self.monto < 0:
            raise ValidationError({"monto": "El monto no puede ser negativo."})

    def __str__(self):
        return self.tipo


class Donacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE)
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donacion de {self.cliente.primer_nombre} {self.cliente.primer_apellido} para {self.fundacion.nombre}"


## MODELO DE ADOPCIONES


class PublicacionAdopcion(models.Model):

    id = models.AutoField(primary_key=True)  # Lo pogo pa que abajo me deje poner el id
    fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)
    direccion = models.ForeignKey(
        Direccion, on_delete=models.CASCADE, null=False, blank=False, default=None
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} {self.titulo} - {self.mascota.nombre}"


class SolicitudAdopcion(models.Model):

    ESTADOS = {
        "Pendiente": "Pendiente",
        "Aceptada": "Aceptada",
        "Rechazada": "Rechazada",
        "Cancelada": "Cancelada",
        "Completada": "Completada",
    }
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(PublicacionAdopcion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField(null=False, blank=False)
    estado = models.CharField(
        max_length=255, null=True, blank=True, choices=ESTADOS, default="Pendiente"
    )

    def __str__(self):
        return f"{self.cliente.primer_nombre} {self.cliente.primer_apellido} - {self.publicacion.titulo}"


class CategoriaPrincipal(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"Categoría principal - {self.nombre}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False)
    categoria_principal = models.ForeignKey(
        CategoriaPrincipal, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Categoría principal - {self.categoria_principal.nombre} | Categoría - {self.nombre}"


class Subcategoria(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"Categoría principal - {self.categoria.categoria_principal.nombre} | Categoría - {self.categoria.nombre} | Subcategoría - {self.nombre}"


class ProductoCategorias(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sub_categoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"Producto - {self.producto.nombre} | Categoría principal {self.sub_categoria.categoria.categoria_principal.nombre} | Categoría - {self.sub_categoria.categoria.nombre} | Subcategoría - {self.sub_categoria.nombre}"
