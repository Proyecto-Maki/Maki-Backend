from django.contrib import admin
from .models import (
    User,
    Cliente,
    Fundacion,
    Mascota,
    Padecimiento,
    Producto,
    ItemCarrito,
    Carrito,
)

# Register your models here.

admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Fundacion)
admin.site.register(Mascota)
admin.site.register(Padecimiento)
admin.site.register([Producto, ItemCarrito, Carrito])
