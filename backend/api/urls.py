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
    path("fundaciones/", FundacionView.as_view(), name="fundaciones"),
    path(
        "fundaciones/localidad/<int:id>/",
        FundacionLocalidadView.as_view(),
        name="fundaciones_localidad",
    ),
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
    path(
        "update_cantidad_producto/",
        update_cantidad_producto,
        name="update_cantidad_producto",
    ),
    path(
        "remove_product_from_cart/",
        remove_product_from_cart,
        name="remove_product_from_cart",
    ),
    ##path("producto/", productos, name="register_producto"),
    ## Carrito
    path("get_estado_carrito", get_estado_carrito, name="get_estado_carrito"),
    ## Reseñas
    path(
        "productos/resenas/<int:id>/",
        ResenasProductoView.as_view(),
        name="resenas_producto",
    ),
    path("resenas/user/<email>/", ResenasUserView.as_view(), name="resenas_user"),
    path("resena/create/", ResenaCreateView.as_view(), name="resena_create"),
    path("resena/update/<int:id>/", ResenaUpdateView.as_view(), name="resena_update"),
    path("resena/delete/<int:id>/", ResenaDeleteView.as_view(), name="resena_delete"),
    ## Pedidos
    path("pedidos/user/<email>/", PedidosUserView.as_view(), name="pedidos_user"),
    path("pedidos/create/", PedidoCreateView.as_view(), name="pedido_create"),
    path("pedidos/update/<int:id>/", PedidoUpdateView.as_view(), name="pedido_update"),
    path("pedidos/delete/<int:id>/", PedidoDeleteView.as_view(), name="pedido_delete"),
    ## Detalle de pedidos
    path(
        "detalle-pedidos/pedido/<int:id>/",
        DetallePedidoView.as_view(),
        name="detalle_pedidos",
    ),
    path(
        "detalles-pedido/pedido/<int:id>/",
        DetallesPedidoView.as_view(),
        name="detalles_pedido",
    ),
    path(
        "detalle-pedidos/create/",
        DetallePedidoCreateView.as_view(),
        name="detalle_pedido_create",
    ),
    path(
        "detalle-pedidos/update/<int:id>/",
        DetallePedidoUpdateView.as_view(),
        name="detalle_pedido_update",
    ),
    path(
        "detalle-pedidos/delete/<int:id>/",
        DetallePedidoDeleteView.as_view(),
        name="detalle_pedido_delete",
    ),
    ## Publicaciones
    path("publicaciones/", PublicacionAdopcionView.as_view(), name="publicaciones"),
    path(
        "publicaciones/fundacion/<email>/",
        PublicacionesAdopcionUserView.as_view(),
        name="publicaciones_fundacion",
    ),
    path(
        "publicaciones/create/",
        PublicacionAdopcionCreateView.as_view(),
        name="publicacion_create",
    ),
    path(
        "publicaciones/<int:id>/",
        PublicacionAdopcionDetailView.as_view(),
        name="publicacion_detail",
    ),
    path(
        "publicaciones/update/<int:id>/",
        PublicacionAdopcionUpdateView.as_view(),
        name="publicacion_update",
    ),
    path(
        "publicaciones/delete/<int:id>/",
        PublicacionAdopcionDeleteView.as_view(),
        name="publicacion_delete",
    ),
    ## Detalle de mascotas
    path(
        "detalle-mascota/create/",
        DetalleMascotaCreateView.as_view(),
        name="detalle_mascota_create",
    ),
    path(
        "detalle-mascota/<int:id>/",
        DetalleMascotaView.as_view(),
        name="detalle_mascota",
    ),
    path(
        "detalle-mascota/update/<int:id>/",
        DetalleMascotaUpdateView.as_view(),
        name="detalle_mascota_update",
    ),
    path(
        "detalle-mascota/delete/<int:id>/",
        DetalleMascotaDeleteView.as_view(),
        name="detalle_mascota_delete",
    ),
    ## Publicaciones de adopcion y detalles - cliente
    path(
        "publicaciones-adopcion/",
        PublicacionAdopcionClienteView.as_view(),
        name="publicaciones_adopcion_cliente",
    ),
]
