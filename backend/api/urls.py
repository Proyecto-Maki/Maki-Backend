from django.urls import path
from .views import FundacionSignupView, ClienteSignupView, CustomTokenObtainPairView, CustomAuthToken, LogoutView, ClienteOnlyView, FundacionOnlyView, VerificarCodigo
# from .views import register_cliente, register_fundacion

urlpatterns = [
    # path('registro/cliente/', register_cliente, name='register_cliente'),
    # path('registro/fundacion/', register_fundacion, name='register_fundacion'),
    path('registro/fundacion/', FundacionSignupView.as_view(), name='register_fundacion'),
    path('registro/cliente/', ClienteSignupView.as_view(), name='register_cliente'),
    path('token/', CustomTokenObtainPairView.as_view(), name='auth-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cliente/dashboard/', ClienteOnlyView.as_view(), name='cliente_only'),
    path('fundacion/dashboard/', FundacionOnlyView.as_view(), name='fundacion_only'),
    path('verify-email/',  VerificarCodigo.as_view(), name='verify-email'),
]