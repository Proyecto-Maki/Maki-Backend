from django.contrib.auth.models import AbstractUser
from django.db import models

class Cliente(AbstractUser):
    direccion = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    password = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, default='default_username')  # Agrega un valor predeterminado aquí

    REQUIRED_FIELDS = ['email']
    #USERNAME_FIELD = 'username'
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='cliente_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='cliente_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.pk and not self.password:
            self.set_password('default_password')
        super().save(*args, **kwargs)

class Mascota(models.Model):
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255)
    raza = models.CharField(max_length=255, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    estado_salud = models.CharField(max_length=255, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fundacion = models.ForeignKey('Fundacion', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Resena(models.Model):
    contenido = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    calificacion = models.IntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(calificacion__gte=1, calificacion__lte=5),
                name="calificacion_rango"
            )
        ]

    def __str__(self):
        return f'Reseña de {self.cliente} para {self.producto}'

class Fundacion(AbstractUser):
    direccion = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    REQUIRED_FIELDS = ['email']
    # USERNAME_FIELD = 'username'
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='fundacion_set',  # Cambia el related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='fundacion_user_set',  # Cambia el related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.pk and not self.password:
            self.set_password('default_password')  # Define un valor predeterminado aquí
        super().save(*args, **kwargs)

class PublicacionAdopcion(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class Pedido(models.Model):
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    fundacion = models.ForeignKey(Fundacion, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(cliente__isnull=False) | models.Q(fundacion__isnull=False),
                name="cliente_o_fundacion"
            )
        ]

    def __str__(self):
        return f'Pedido {self.id}'

class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.cantidad} x {self.producto}'

class Cuidador(models.Model):
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.nombre

class SolicitudCuidado(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=255)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cuidador = models.ForeignKey(Cuidador, on_delete=models.CASCADE)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)

    def __str__(self):
        return f'Solicitud de {self.cliente} para {self.mascota}'
