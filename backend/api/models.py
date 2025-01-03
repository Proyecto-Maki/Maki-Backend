from django.conf import settings
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
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
    direccion = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    saldo = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.BigIntegerField(unique=True,null=True, blank=True)
    primer_nombre = models.CharField(max_length=255, null=True, blank=True)
    segundo_nombre = models.CharField(max_length=255, null=True, blank=True)
    primer_apellido = models.CharField(max_length=255, null=True, blank=True)
    segundo_apellido = models.CharField(max_length=255, null=True, blank=True)
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


# MODELO DE MASCOTA

class Mascota(models.Model):
    # la mascota tiene su primaty key autoincremental

    ESTADOS = {
        'Saludable': 'Saludable',
        'Enfermo': 'Enfermo',
        'Recuperacion': 'Recuperacion',
    }

    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    nombre = models.CharField(max_length=255, null=False, blank=False)
    tipo = models.CharField(max_length=255, null=False, blank=False)
    raza = models.CharField(max_length=255, null=False, blank=False)
    edad = models.IntegerField(null=False, blank=False)
    estado_salud = models.CharField(max_length=255, null=False, blank=False, choices=ESTADOS)

    TAMANOS = {
        'P': 'Pequeño',
        'M': 'Mediano',
        'G': 'Grande',
    }
    tamano = models.CharField(max_length=1, null=False, blank=False, choices=TAMANOS)
    peso = models.DecimalField(max_digits=3, decimal_places=2, null=False, blank=False)
    imagen = models.ImageField(upload_to='mascotas/', null=True, blank=True) # Esta es de prueba


    def __str__(self):
        return self.nombre

## MODELO DE PADECIMIENTO

class Padecimiento(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    padecimiento = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"{self.mascota.nombre} - {self.padecimiento}"

## MODELO DE PRODUCTO

class Producto(models.Model):
    nombre = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=False, blank=False)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=255, null=False, blank=False)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True) # Esta es de prueba

    def __str__(self):
        return self.nombre

## MODELO DE PEDIDO

class Descuento(models.Model):
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=False, blank=False)

    def __str__(self):
        return f"{self.descripcion} - {self.porcentaje}%"

class Pedido(models.Model):

    ESTADOS = {
        'Preparación': 'Preparación',
        'Entregado': 'Entregado',
        'Transito': 'Transito',
        'Cancelado': 'Cancelado',
    }
    id = models.AutoField(primary_key=True) # Lo pogo pa que abajo me deje poner el id
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True, null=False, blank=False)
    estado = models.CharField(max_length=255, null=False, blank=False, choices=ESTADOS)
    descuento = models.ForeignKey(Descuento, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=False, blank=False)

    def __str__(self):
        return self.id
    
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
    

## MODELO DE CUIDADOR

class Cuidador(models.Model):
    cedula = models.BigIntegerField(unique=True, null=False, blank=False)
    primer_nombre = models.CharField(max_length=255, null=False, blank=False)
    segundo_nombre = models.CharField(max_length=255, null=True, blank=True)
    primer_apellido = models.CharField(max_length=255, null=False, blank=False)
    segundo_apellido = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=10, null=False, blank=False)
    direccion = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    ocupacion = models.CharField(max_length=255, null=False, blank=False)
    experiencia = models.TextField(null=False, blank=False)
    descripcion_servicio = models.TextField(null=False, blank=False)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"
    
## MODELO DE SOLICITUD DE CUIDADO

class SolicitudCuidado(models.Model):
    ESTADOS = {
        'Pendiente': 'Pendiente',
        'Aceptada': 'Aceptada',
        'Rechazada': 'Rechazada',
        'Cancelada': 'Cancelada',
        'Completada': 'Completada',
    }

    id = models.AutoField(primary_key=True) # Lo pogo pa que abajo me deje poner el id
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_fin = models.DateField(null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)
    estado = models.CharField(max_length=255, null=False, blank=False, choices=ESTADOS)


## MODELO DE RESEÑA

class Resena(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    calificacion = models.IntegerField(null=False, blank=False) 
    comentario = models.TextField(null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(calificacion__gte=1, calificacion__lte=5),
                name="calificacion_rango"
            )
        ]

    def __str__(self):
        return f'Reseña de {self.user.id} para {self.producto.nombre}'

## MODELO DE DONACION

class Tarjeta(models.Model):
    tipo = models.CharField(max_length=255, null=False, blank=False, primary_key=True)
    monto = models.DecimalField(max_digits=7, decimal_places=2, default=0.00, null=False, blank=False)

    def __str__(self):
        return self.tipo

class Donacion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE)
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'Donacion de {self.cliente.primer_nombre} {self.cliente.primer_apellido} para {self.fundacion.nombre}'


## MODELO DE ADOPCIONES

class PublicacionAdopcion(models.Model):
    
    fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.titulo} - {self.mascota.nombre}'
    
class SolicitudAdopcion(models.Model):

    ESTADOS = {
        'Pendiente': 'Pendiente',
        'Aceptada': 'Aceptada',
        'Rechazada': 'Rechazada',
        'Cancelada': 'Cancelada',
        'Completada': 'Completada',
    }
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(PublicacionAdopcion, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    motivo = models.TextField(null=False, blank=False)
    estado = models.CharField(max_length=255, null=False, blank=False, choices=ESTADOS)

    def __str__(self):
        return f'{self.cliente.primer_nombre} {self.cliente.primer_apellido} - {self.publicacion.titulo}'


