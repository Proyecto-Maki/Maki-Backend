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

# class ClienteManager(BaseUserManager):
#     def get_queryset(self, *args, **kwargs):
#         results = super().get_queryset(*args, **kwargs)
#         return results.filter(role=User.Role.CLIENTE)

# class Cliente(User):
#     base_role = User.Role.CLIENTE
#     cliente = ClienteManager()
#     class Meta:
#         proxy = True

#     def welcome(self):
#         return "Solo para clientes"
    
# @receiver(post_save, sender=Cliente)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created and instance.role == User.Role.CLIENTE:
#         ClienteProfile.objects.create(user=instance)
# class ClienteProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     cliente_id = models.AutoField(primary_key=True)
#     direccion = models.CharField(max_length=255, null=True, blank=True)
#     telefono = models.CharField(max_length=20, null=True, blank=True)
#     saldo = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
#     email = models.EmailField(unique=True)

# class FundacionManager(BaseUserManager):
#     def get_queryset(self, *args, **kwargs):
#         results = super().get_queryset(*args, **kwargs)
#         return results.filter(role=User.Role.FUNDACION)

# class Fundacion(User):
#     base_role = User.Role.FUNDACION
#     fundacion = FundacionManager()
#     class Meta:
#         proxy = True

#     def welcome(self):
#         return "Solo para fundaciones"

# class Cliente(AbstractUser):
#     direccion = models.CharField(max_length=255, null=True, blank=True)
#     telefono = models.CharField(max_length=20, null=True, blank=True)
#     saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     password = models.CharField(max_length=128, null=True, blank=True)
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=150, unique=True, default='default_username')  # Agrega un valor predeterminado aquí

#     REQUIRED_FIELDS = ['email']
#     #USERNAME_FIELD = 'username'
#     USERNAME_FIELD = 'email'
#     EMAIL_FIELD = 'email'

#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='cliente_set',
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='cliente_user_set',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )

#     def __str__(self):
#         return f'Cliente: {self.username}'

#     def save(self, *args, **kwargs):
#         if not self.pk and not self.password:
#             self.set_password('default_password')
#         super().save(*args, **kwargs)

# class Mascota(models.Model):
#     nombre = models.CharField(max_length=255)
#     tipo = models.CharField(max_length=255)
#     raza = models.CharField(max_length=255, null=True, blank=True)
#     edad = models.IntegerField(null=True, blank=True)
#     estado_salud = models.CharField(max_length=255, null=True, blank=True)
#     cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
#     fundacion = models.ForeignKey('Fundacion', on_delete=models.CASCADE, null=True, blank=True)

#     def __str__(self):
#         return self.nombre

# class Producto(models.Model):
#     nombre = models.CharField(max_length=255)
#     descripcion = models.TextField(null=True, blank=True)
#     precio = models.DecimalField(max_digits=10, decimal_places=2)
#     stock = models.IntegerField(default=0)

#     def __str__(self):
#         return self.nombre

# class Resena(models.Model):
#     contenido = models.TextField()
#     fecha = models.DateField(auto_now_add=True)
#     likes = models.IntegerField(default=0)
#     calificacion = models.IntegerField()
#     cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

#     class Meta:
#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(calificacion__gte=1, calificacion__lte=5),
#                 name="calificacion_rango"
#             )
#         ]

#     def __str__(self):
#         return f'Reseña de {self.cliente} para {self.producto}'

# class Fundacion(AbstractUser):
#     direccion = models.CharField(max_length=255, null=True, blank=True)
#     telefono = models.CharField(max_length=20, null=True, blank=True)
#     email = models.EmailField(unique=True)
#     saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

#     REQUIRED_FIELDS = ['email']
#     # USERNAME_FIELD = 'username'
#     USERNAME_FIELD = 'email'
#     EMAIL_FIELD = 'email'

#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='fundacion_set',  # Cambia el related_name
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='fundacion_user_set',  # Cambia el related_name
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )

#     def __str__(self):
#         return f'Fundacion: {self.username}'

#     def save(self, *args, **kwargs):
#         if not self.pk and not self.password:
#             self.set_password('default_password')  # Define un valor predeterminado aquí
#         super().save(*args, **kwargs)

# class PublicacionAdopcion(models.Model):
#     titulo = models.CharField(max_length=255)
#     descripcion = models.TextField(null=True, blank=True)
#     fecha = models.DateField(auto_now_add=True)
#     fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE)
#     mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.titulo

# class Pedido(models.Model):
#     fecha = models.DateField(auto_now_add=True)
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
#     fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE, null=True, blank=True)

#     class Meta:
#         constraints = [
#             models.CheckConstraint(
#                 check=models.Q(cliente__isnull=False) | models.Q(fundacion__isnull=False),
#                 name="cliente_o_fundacion"
#             )
#         ]

#     def __str__(self):
#         return f'Pedido {self.id}'

# class PedidoProducto(models.Model):
#     pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     cantidad = models.IntegerField()
#     precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f'{self.cantidad} x {self.producto}'

# class Cuidador(models.Model):
#     nombre = models.CharField(max_length=255)
#     correo = models.EmailField(unique=True)
#     telefono = models.CharField(max_length=20, null=True, blank=True)

#     def __str__(self):
#         return self.nombre

# class SolicitudCuidado(models.Model):
#     fecha_inicio = models.DateField()
#     fecha_fin = models.DateField()
#     estado = models.CharField(max_length=255)
#     cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
#     cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
#     mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)

#     def __str__(self):
#         return f'Solicitud de {self.cliente} para {self.mascota}'
