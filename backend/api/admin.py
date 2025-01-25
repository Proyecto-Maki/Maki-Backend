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
    Resena,
    Pedido,
    Descuento,
    DetallePedido,
    Localidad,
    Direccion,
    PublicacionAdopcion,
    DetalleMascota,
    SolicitudAdopcion
)

# Register your models here.

admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Fundacion)
admin.site.register(Mascota)
admin.site.register(Padecimiento)
admin.site.register([Producto, ItemCarrito, Carrito])
admin.site.register(Resena)
admin.site.register(Pedido)
admin.site.register(Descuento)
admin.site.register(DetallePedido)
admin.site.register(Localidad)
admin.site.register(Direccion)
admin.site.register(PublicacionAdopcion)
admin.site.register(DetalleMascota)
admin.site.register(SolicitudAdopcion)



