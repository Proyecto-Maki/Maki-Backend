from django.urls import path
from .views import *
# from .views import register_cliente, register_fundacion

urlpatterns = [
    # path('registro/cliente/', register_cliente, name='register_cliente'),
    # path('registro/fundacion/', register_fundacion, name='register_fundacion'),
    path('registro/fundacion/', FundacionSignupView.as_view(), name='register_fundacion'),
    path('registro/cliente/', ClienteSignupView.as_view(), name='register_cliente'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cliente/dashboard/', ClienteOnlyView.as_view(), name='cliente_only'),
    path('fundacion/dashboard/', FundacionOnlyView.as_view(), name='fundacion_only'),
    path('verify-email/',  VerificarCodigo.as_view(), name='verify-email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPassword.as_view(), name='password-reset-complete'),
    path('current-user/', CurrentUserView.as_view(), name='current-user'),

    ## Mascota

    path('registro/mascota/', MascotaCreateView.as_view(), name='register_mascota'),
    path('mascotas/<email>/', MascotasUserView.as_view(), name='mascotas_user'),
]