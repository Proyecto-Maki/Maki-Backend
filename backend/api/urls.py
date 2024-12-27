from django.urls import path
from .views import FundacionSignupView, ClienteSignupView
# from .views import register_cliente, register_fundacion

urlpatterns = [
    # path('registro/cliente/', register_cliente, name='register_cliente'),
    # path('registro/fundacion/', register_fundacion, name='register_fundacion'),
    path('registro/fundacion/', FundacionSignupView.as_view(), name='register_fundacion'),
    path('registro/cliente/', ClienteSignupView.as_view(), name='register_cliente'),
]