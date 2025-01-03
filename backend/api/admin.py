from django.contrib import admin
from .models import User, Cliente, Fundacion, Mascota
# Register your models here.

admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Fundacion)
admin.site.register(Mascota)

