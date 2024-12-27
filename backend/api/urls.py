from django.urls import path
from .views import register_cliente, register_fundacion

urlpatterns = [
    path('registro/cliente/', register_cliente, name='register_cliente'),
    path('registro/fundacion/', register_fundacion, name='register_fundacion'),
]