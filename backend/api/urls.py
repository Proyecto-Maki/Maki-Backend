from django.urls import path
from .views import *

# from .views import register_cliente, register_fundacion

urlpatterns = [
    path("test-email/", SendTestEmail, name="test-email"),
    # path('registro/cliente/', register_cliente, name='register_cliente'),
    # path('registro/fundacion/', register_fundacion, name='register_fundacion'),
    path(
        "registro/fundacion/", FundacionSignupView.as_view(), name="register_fundacion"
    ),
    path("registro/cliente/", ClienteSignupView.as_view(), name="register_cliente"),
    path("login/", CustomTokenObtainPairView.as_view(), name="auth-token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("cliente/dashboard/", ClienteOnlyView.as_view(), name="cliente_only"),
    path("fundacion/dashboard/", FundacionOnlyView.as_view(), name="fundacion_only"),
    path("verify-email/", VerificarCodigo.as_view(), name="verify-email"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirm.as_view(),
        name="password-reset-confirm",
    ),
    path("set-new-password/", SetNewPassword.as_view(), name="password-reset-complete"),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
    ## Cliente
    path("cliente-profile/", ClienteDetailView.as_view(), name="cliente-profile"),
    path(
        "cliente-profile-update/",
        ClienteUpdateView.as_view(),
        name="cliente-profile-update",
    ),
    path(
        "cliente-profile-delete/",
        ClienteDeleteView.as_view(),
        name="cliente-profile-delete",
    ),
    ## Fundacion
    path("fundacion-profile/", FundacionDetailView.as_view(), name="fundacion-profile"),
    path(
        "fundacion-profile-update/",
        FundacionUpdateView.as_view(),
        name="fundacion-profile-update",
    ),
    path(
        "fundacion-profile-delete/",
        FundacionDeleteView.as_view(),
        name="fundacion-profile-delete",
    ),
    ## Mascota
    path("registro/mascota/", MascotaCreateView.as_view(), name="register_mascota"),
    path("mascotas/<email>/", MascotasUserView.as_view(), name="mascotas_user"),
    path(
        "mascotas/update/<int:id>/", MascotaUpdateView.as_view(), name="mascota_update"
    ),
    path(
        "mascotas/delete/<int:id>/", MascotaDeleteView.as_view(), name="mascota_delete"
    ),
    path(
        "mascotas/detalle/<int:id>/", MascotaDetailView.as_view(), name="mascota_detail"
    ),
    path(
        "registro/mascota/padecimiento/",
        PadecimientoCreateView.as_view(),
        name="register_padecimiento",
    ),
    path(
        "padecimientos/mascota/<int:id>/",
        PadecimientoDetailView.as_view(),
        name="padecimientos_mascota",
    ),
    path(
        "padecimientos/update/<int:id>/",
        PadecimientoUpdateView.as_view(),
        name="padecimiento_update",
    ),
    path(
        "padecimientos/delete/<int:id>/",
        PadecimientoDeleteView.as_view(),
        name="padecimiento_delete",
    ),
    ## Productos
    path("productos/", ProductoListView.as_view(), name="productos_list"),
    path(
        "productos/<slug:slug>/", ProductoDetailView.as_view(), name="producto-detalle"
    ),
    path("agregar_producto/", agregar_producto, name="agregar_producto"),
    path("producto_en_carrito/", producto_en_carrito, name="producto_en_carrito"),
    ##path("producto/", productos, name="register_producto"),
]
