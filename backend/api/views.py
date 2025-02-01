from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import *
from rest_framework.views import APIView
from .permissions import IsClienteUser, IsFundacionUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
from rest_framework.exceptions import PermissionDenied

# from .forms import RegistroForm, ClienteCreationForm, FundacionCreationForm
from .models import *

# from .utils import send_code_to_user
from .new_utils import send_code_to_user, send_test_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

import mercadopago
import json


@csrf_exempt
def create_preference(request):
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        try:
            body = json.loads(
                request.body
            )  # Asegúrate de cargar correctamente los datos del cuerpo de la solicitud
            preference_data = {
                "items": body["items"],
                "back_urls": {
                    "success": "https://makishop.live/pending",
                    "failure": "https://makishop.live/pending",
                    "pending": "https://makishop.live/pending",
                },
                "auto_return": "approved",
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            # Devuelve el init_point junto con el ID de la preferencia
            return JsonResponse(
                {
                    "id": preference.get("id"),
                    "init_point": preference.get("init_point"),
                }
            )

        except Exception as e:
            print(f"Error al crear la preferencia: {e}")
            return JsonResponse({"error": "Error al crear la preferencia"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def mercadopago_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_id = data.get("data", {}).get("id", None)

            if not payment_id:
                return JsonResponse(
                    {"error": "No se recibió un ID de pago"}, status=400
                )

            # Consultar el estado del pago
            payment = sdk.payment().get(payment_id)
            status = payment["response"]["status"]

            print(f"Pago recibido. ID: {payment_id}, Estado: {status}")

            if status == "approved":
                # Obtener los datos adicionales (por ejemplo, el ID del usuario)
                user_id = payment["response"].get("metadata", {}).get("user_id", None)

                if not user_id:
                    return JsonResponse({"error": "No se encontró user_id"}, status=400)

                # Obtener el usuario
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return JsonResponse({"error": "Usuario no encontrado"}, status=400)

                # Obtener el carrito del usuario
                carrito = Carrito.objects.filter(user=user).first()

                if not carrito:
                    return JsonResponse({"error": "Carrito no encontrado"}, status=400)

                # Crear un nuevo Pedido
                nuevo_pedido = Pedido.objects.create(
                    user=user, total=carrito.total, estado="Preparación"
                )

                # Agregar productos al Pedido
                for item in carrito.carritoproducto_set.all():
                    DetallePedido.objects.create(
                        pedido=nuevo_pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                    )

                # Vaciar el carrito después de procesar el pedido
                carrito.carritoproducto_set.all().delete()

                return JsonResponse({"message": "Pedido creado con éxito"}, status=201)

            return JsonResponse({"message": "Pago no aprobado"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@api_view(["GET"])
def SendTestEmail(request):
    try:
        response = send_test_email()
        return Response({"message": response["message"]})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClienteSignupView(generics.ListCreateAPIView):
    # serializer_class = ClienteSignupSerializer
    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     return Response({
    #             "user": UserSerializer(user, context=self.get_serializer_context()).data,
    #             "token": Token.objects.get(user=user).key,
    #             "message": "Cliente creado exitosamente",
    #         })
    queryset = Cliente.objects.all()
    serializer_class = ClienteSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_code_to_user(user.email)
            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "message": "Cliente creado exitosamente. Se envió un código de verificación a tu correo electrónico",
                },
                status=status.HTTP_201_CREATED,
            )

        errores = {}
        for key, value in serializer.errors.items():
            errores[key] = ", ".join(value)

        mensaje = " | ".join([f"{key}: {value}" for key, value in errores.items()])
        return Response(
            {
                "error": serializer.errors,
                "detail": mensaje,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class FundacionSignupView(generics.ListCreateAPIView):

    queryset = Fundacion.objects.all()
    serializer_class = FundacionSignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_code_to_user(user.email)
            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "message": "Fundacion creada exitosamente. Se envió un código de verificación a tu correo electrónico",
                },
                status=status.HTTP_201_CREATED,
            )
        errores = {}
        for key, value in serializer.errors.items():
            errores[key] = ", ".join(value)

        mensaje = " | ".join([f"{key}: {value}" for key, value in errores.items()])
        return Response(
            {
                "error": serializer.errors,
                "detail": mensaje,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # serializer_class = FundacionSignupSerializer
    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     return Response({
    #             "user": UserSerializer(user, context=self.get_serializer_context()).data,
    #             "token": Token.objects.get(user=user).key,
    #             "message": "Fundacion creada exitosamente",
    #         })


class VerificarCodigo(generics.GenericAPIView):
    def post(self, request):
        otpcode = request.data.get("otp")
        try:
            user_code_obj = OneTimePassword.objects.get(code=otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response(
                    {"message": "Usuario verificado exitosamente"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Código no es válido. Usuario ya verificado"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except OneTimePassword.DoesNotExist:
            return Response(
                {"message": "Código no es válido"}, status=status.HTTP_404_NOT_FOUND
            )


class CustomAuthToken(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        credentials = {"email": attrs.get("email"), "password": attrs.get("password")}

        user = authenticate(**credentials)
        if user:
            if not user.is_active:
                raise exceptions.AuthenticationFailed("La cuenta no está activa.")
            if not user.is_verified:
                raise exceptions.AuthenticationFailed("La cuenta no está verificada.")

            data = {}
            refresh = self.get_token(user)
            data["email"] = user.email
            data["is_cliente"] = user.is_cliente
            data["is_fundacion"] = user.is_fundacion
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return {"data": data, "message": "¡Bienvenido a Maki!"}
        else:
            raise exceptions.AuthenticationFailed(
                "No es posible iniciar sesión con esas credenciales."
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomAuthToken


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClienteOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class FundacionOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "message": "Se envió a tu correo electrónico un link para restablecer tu contraseña"
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirm(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"message": "Token no es válido o está expirado"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {
                    "success": True,
                    "message": "Credenciales válidas",
                    "uidb6": uidb64,
                    "token": token,
                },
                status=status.HTTP_200_OK,
            )
        except DjangoUnicodeDecodeError:
            return Response(
                {"message": "Token no es válido o está expirado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class SetNewPassword(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Contraseña restablecida exitosamente"},
                status=status.HTTP_200_OK,
            )
        # serializer.is_valid(raise_exception=True)
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error para restablecer la contraseña",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CurrentUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "email": user.email,
                "is_cliente": user.is_cliente,
                "is_fundacion": user.is_fundacion,
            }
        )


class ClienteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()

    def get_object(self):
        email = self.request.query_params.get("email")
        if not email:
            raise ValueError("Debes proporcionar un parámetro 'email' en la consulta.")

        # Busca el usuario con el email proporcionado
        user = get_object_or_404(User, email=email)

        # Busca el cliente asociado al usuario encontrado
        cliente = get_object_or_404(self.queryset, user=user)

        return cliente


class ClienteUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = ClienteSerializer

    def get_object(self):
        email = self.request.query_params.get("email")
        if not email:
            raise serializers.ValidationError(
                {"error": "Se debe proporcionar un parámetro 'email'."}
            )
        user = get_object_or_404(User, email=email)
        cliente = get_object_or_404(Cliente, user=user)
        return cliente

    def put(self, request, *args, **kwargs):
        cliente = self.get_object()
        serializer = self.get_serializer(cliente, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClienteDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all()

    def get_object(self):
        cliente = get_object_or_404(Cliente, user=self.request.user)
        return cliente

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()


class FundacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = FundacionSerializer
    queryset = Fundacion.objects.all()

    def get_object(self):
        email = self.request.query_params.get("email")
        if not email:
            raise ValueError("Debes proporcionar un parámetro 'email' en la consulta.")
        user = get_object_or_404(User, email=email)
        fundacion = get_object_or_404(self.queryset, user=user)
        return fundacion

    def put(self, request, *args, **kwargs):
        fundacion = self.get_object()
        serializer = self.get_serializer(fundacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundacionUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = FundacionSerializer

    def get_object(self):
        email = self.request.query_params.get("email")
        if not email:
            raise serializers.ValidationError(
                {"error": "Se debe proporcionar un parámetro 'email'."}
            )
        user = get_object_or_404(User, email=email)
        fundacion = get_object_or_404(Fundacion, user=user)
        return fundacion

    def put(self, request, *args, **kwargs):
        fundacion = self.get_object()
        serializer = self.get_serializer(fundacion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundacionDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = FundacionSerializer
    queryset = Fundacion.objects.all()

    def get_object(self):
        fundacion = get_object_or_404(Fundacion, user=self.request.user)
        return fundacion

    def perform_destroy(self, instance):
        user = instance.user
        instance.delete()
        user.delete()


class FundacionView(generics.ListAPIView):
    queryset = Fundacion.objects.all()
    serializer_class = FundacionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Fundacion.objects.select_related("user").all()


class FundacionLocalidadView(generics.ListAPIView):
    serializer_class = FundacionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        id_localidad = self.kwargs.get("id")
        localidad = get_object_or_404(Localidad, id=id_localidad)
        return Fundacion.objects.select_related("user__direccion__localidad").filter(
            user__direccion__localidad=localidad
        )


class MascotaCreateView(generics.ListCreateAPIView):
    queryset = Mascota.objects.all()
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = MascotaSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            mascota = serializer.save()
            return Response(
                {"id": mascota.id, "message": "Mascota creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al crear la mascota",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class MascotasUserView(generics.ListAPIView):
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return Mascota.objects.filter(user=user)


class MascotaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(Mascota, id=id)


class MascotaUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Mascota.objects.get(id=id)
        except Mascota.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        mascota = self.get_object(id)
        if not mascota:
            return Response(
                {"message": "Mascota no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )

        if mascota.user != request.user:
            raise PermissionDenied("No tienes permisos para editar esta mascota")

        serializer = MascotaSerializer(mascota, data=request.data)

        if serializer.is_valid():
            serializer.update(mascota, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MascotaDeleteView(generics.DestroyAPIView):
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        mascota = get_object_or_404(Mascota, id=id)
        if mascota.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar esta mascota"
            )
        return mascota

    def perform_destroy(self, instance):
        instance.delete()


@api_view(["GET"])
def productos(request):
    productos = Producto.objects.all()
    serializer = ProductoSerializer(productos, many=True)
    response = Response(serializer.data)
    response["Access-Control-Allow-Origin"] = "*"
    return response


# productos


@api_view(["POST"])
def agregar_producto(request):
    try:
        print(
            "Datos recibidos en el backend:", request.data
        )  # Imprime los datos recibidos
        codigo = request.data.get("codigo")
        id_producto = request.data.get("id_producto")

        # Verifica si los datos son válidos
        if not codigo or not id_producto:
            return Response(
                {"error": "Faltan datos obligatorios: 'codigo' o 'id_producto'"},
                status=400,
            )

        carrito, creado = Carrito.objects.get_or_create(codigo=codigo)
        producto = get_object_or_404(Producto, id=id_producto)

        item_carrito, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito, producto=producto
        )
        item_carrito.cantidad += 1
        item_carrito.save()

        serializer = ItemCarritoSerializer(item_carrito)
        return Response(
            {
                "data": serializer.data,
                "message": "Producto agregado al carrito exitosamente",
            },
            status=201,
        )
    except Exception as e:
        print("Error en el servidor:", str(e))  # Log para depuración
        return Response({"error": str(e)}, status=400)


class ProductoDetailView(generics.RetrieveAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Producto, slug=slug)


class ProductoListView(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]


# class ProductosView(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Producto.objects.all()
#     serializer_class = ProductoSerializer


class PadecimientoCreateView(generics.ListCreateAPIView):
    queryset = Padecimiento.objects.all()
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = PadecimientoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Padecimiento creado exitosamente"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al crear el padecimiento",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PadecimientoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PadecimientoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id_mascota = self.kwargs.get("id")
        mascota = get_object_or_404(Mascota, id=id_mascota)
        return get_object_or_404(Padecimiento, mascota=mascota)


class PadecimientoUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Padecimiento.objects.get(id=id)
        except Padecimiento.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        id_mascota = self.kwargs.get("id")
        mascota = get_object_or_404(Mascota, id=id_mascota)
        padecimiento = Padecimiento.objects.get(mascota=mascota)
        if not padecimiento:
            return Response(
                {"message": "Padecimiento no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if padecimiento.mascota.user != request.user:
            raise PermissionDenied("No tienes permisos para editar este padecimiento")
        serializer = PadecimientoSerializer(padecimiento, data=request.data)
        if serializer.is_valid():
            serializer.update(padecimiento, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PadecimientoDeleteView(generics.DestroyAPIView):
    serializer_class = PadecimientoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        padecimiento = get_object_or_404(Padecimiento, id=id)
        if padecimiento.mascota.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar este padecimiento"
            )
        return padecimiento

    def perform_destroy(self, instance):
        instance.delete()


@api_view(["GET"])
def producto_en_carrito(request):
    codigo = request.query_params.get("codigo")
    id_producto = request.query_params.get("id_producto")

    carrito = get_object_or_404(Carrito, codigo=codigo)
    producto = Producto.objects.get(id=id_producto)

    producto_existe_en_carro = ItemCarrito.objects.filter(
        carrito=carrito, producto=producto
    ).exists()

    return Response({"producto_en_carrito": producto_existe_en_carro})


@api_view(["GET"])
def get_estado_carrito(request):
    codigo_carrito = request.query_params.get("codigo_carrito")
    if not codigo_carrito:
        return Response(
            {"error": "El código del carrito no fue proporcionado."}, status=400
        )

    carrito = get_object_or_404(Carrito, codigo=codigo_carrito, pagado=False)
    items_carrito = ItemCarrito.objects.filter(carrito=carrito)
    serializer = ItemCarritoSerializer(items_carrito, many=True)

    return Response({"codigo_carrito": carrito.codigo, "productos": serializer.data})


@api_view(["POST"])
def update_cantidad_producto(request):
    try:
        print("Datos recibidos:", request.data)

        # Extraer datos
        codigo_carrito = request.data.get("codigo_carrito")
        id_producto = request.data.get("producto_id")
        nueva_cantidad = request.data.get("cantidad")

        # Validar datos
        if not codigo_carrito or not id_producto or nueva_cantidad is None:
            return JsonResponse(
                {
                    "error": "Datos incompletos. Se requieren 'codigo_carrito', 'producto_id' y 'cantidad'."
                },
                status=400,
            )

        if nueva_cantidad < 1:
            return JsonResponse(
                {"error": "La cantidad debe ser mayor o igual a 1."}, status=400
            )

        # Verificar que el carrito existe
        carrito = get_object_or_404(Carrito, codigo=codigo_carrito)
        print("Carrito encontrado:", carrito)

        # Verificar que el producto está asociado al carrito
        try:
            item_carrito = ItemCarrito.objects.get(
                carrito=carrito, producto_id=id_producto
            )
            print("Item encontrado en el carrito:", item_carrito)
        except ItemCarrito.DoesNotExist:
            return JsonResponse(
                {"error": f"El producto con ID {id_producto} no está en el carrito."},
                status=404,
            )

        # Actualizar la cantidad
        item_carrito.cantidad = nueva_cantidad
        item_carrito.full_clean()  # Validar modelo
        item_carrito.save()
        print("Cantidad actualizada:", item_carrito.cantidad)

        return JsonResponse(
            {"message": "Cantidad actualizada correctamente"}, status=200
        )

    except ValidationError as e:
        return JsonResponse({"error": e.message_dict}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(["POST"])
def remove_product_from_cart(request):
    try:
        print("Datos recibidos para eliminar producto:", request.data)

        codigo_carrito = request.data.get("codigo_carrito")
        producto_id = request.data.get("producto_id")

        if not codigo_carrito or not producto_id:
            return Response(
                {
                    "error": "Datos incompletos: se requiere 'codigo_carrito' y 'producto_id'."
                },
                status=400,
            )

        carrito = get_object_or_404(Carrito, codigo=codigo_carrito)
        item_carrito = get_object_or_404(
            ItemCarrito, carrito=carrito, producto_id=producto_id
        )

        item_carrito.delete()
        return Response(
            {"message": "Producto eliminado del carrito exitosamente."}, status=200
        )
    except Exception as e:
        print(f"Error al eliminar producto: {str(e)}")
        return Response({"error": str(e)}, status=500)


### RESEÑAS


class ResenaCreateView(generics.ListCreateAPIView):
    queryset = Resena.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ResenaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Reseña creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al crear la reseña",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResenasUserView(generics.ListAPIView):
    serializer_class = ResenaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return Resena.objects.filter(user=user)


class ResenasProductoView(generics.ListAPIView):
    serializer_class = ResenaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        id_producto = self.kwargs.get("id")
        producto = get_object_or_404(Producto, id=id_producto)
        return Resena.objects.filter(producto=producto)


class ResenaUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Resena.objects.get(id=id)
        except Resena.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        resena = self.get_object(id)
        if not resena:
            return Response(
                {"message": "Reseña no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
        if resena.user != request.user:
            raise PermissionDenied("No tienes permisos para editar esta reseña")
        serializer = ResenaSerializer(resena, data=request.data)
        if serializer.is_valid():
            serializer.update(resena, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResenaDeleteView(generics.DestroyAPIView):
    serializer_class = ResenaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        resena = get_object_or_404(Resena, id=id)
        if resena.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar esta reseña"
            )
        return resena

    def perform_destroy(self, instance):
        instance.delete()


## PEDIDOS


class PedidoCreateView(generics.ListCreateAPIView):
    queryset = Pedido.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PedidoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Pedido creado exitosamente"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al crear el pedido",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DetallePedidoCreateView(generics.ListCreateAPIView):
    queryset = DetallePedido.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DetallePedidoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Detalle de pedido creado exitosamente"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al crear el detalle de pedido",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PedidosUserView(generics.ListAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return Pedido.objects.filter(user=user)


class DetallePedidoView(generics.ListAPIView):
    serializer_class = DetallePedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id_pedido = self.kwargs.get("id")
        pedido = get_object_or_404(Pedido, id=id_pedido)
        return DetallePedido.objects.filter(pedido=pedido)


class DetallesPedidoView(generics.ListAPIView):
    serializer_class = DetallePedidoConProductoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        id_pedido = self.kwargs.get("id")
        pedido = get_object_or_404(Pedido, id=id_pedido)
        return DetallePedido.objects.filter(pedido=pedido).select_related("producto")


class PedidoUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Pedido.objects.get(id=id)
        except Pedido.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        pedido = self.get_object(id)
        if not pedido:
            return Response(
                {"message": "Pedido no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
        if pedido.user != request.user:
            raise PermissionDenied("No tienes permisos para editar este pedido")
        serializer = PedidoSerializer(pedido, data=request.data)
        if serializer.is_valid():
            serializer.update(pedido, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PedidoDeleteView(generics.DestroyAPIView):
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        pedido = get_object_or_404(Pedido, id=id)
        if pedido.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar este pedido"
            )
        return pedido

    def perform_destroy(self, instance):
        instance.delete()


class DetallePedidoUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return DetallePedido.objects.get(id=id)
        except DetallePedido.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        detalle_pedido = self.get_object(id)
        if not detalle_pedido:
            return Response(
                {"message": "Detalle de pedido no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if detalle_pedido.pedido.user != request.user:
            raise PermissionDenied(
                "No tienes permisos para editar este detalle de pedido"
            )
        serializer = DetallePedidoSerializer(detalle_pedido, data=request.data)
        if serializer.is_valid():
            serializer.update(detalle_pedido, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetallePedidoDeleteView(generics.DestroyAPIView):
    serializer_class = DetallePedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        id = self.kwargs.get("id")
        detalle_pedido = get_object_or_404(DetallePedido, id=id)
        if detalle_pedido.pedido.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar este detalle de pedido"
            )
        return detalle_pedido

    def perform_destroy(self, instance):
        instance.delete()


## PUBLICACION_ADOPCION - PARA LA FUNDACIÓN


## Esta vista es para la creación
class PublicacionAdopcionCreateView(generics.ListCreateAPIView):
    queryset = PublicacionAdopcion.objects.all()
    permissions_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = PublicacionAdopcionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Publicación de adopción creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al crear la publicación de adopción",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


## Esta vista es para listar las publicaciones de adopción de una fundación (para la misma fundación)
class PublicacionesAdopcionUserView(generics.ListAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return PublicacionAdopcion.objects.filter(user=user)


## Esta vista es para listar todas las publicaciones de adopción (sin importar la fundación)
class PublicacionAdopcionView(generics.ListAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return PublicacionAdopcion.objects.all()


## Esta vista es para ver el detalle de una publicación de adopción
class PublicacionAdopcionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(PublicacionAdopcion, id=id)


## Esta vista es para actualizar una publicación de adopción
class PublicacionAdopcionUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_object(self, id):
        try:
            return PublicacionAdopcion.objects.get(id=id)
        except PublicacionAdopcion.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        publicacion_adopcion = self.get_object(id)
        if not publicacion_adopcion:
            return Response(
                {"message": "Publicación de adopción no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if publicacion_adopcion.user != request.user:
            raise PermissionDenied(
                "No tienes permisos para editar esta publicación de adopción"
            )
        serializer = PublicacionAdopcionSerializer(
            publicacion_adopcion, data=request.data
        )
        if serializer.is_valid():
            serializer.update(publicacion_adopcion, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


## Esta vista es para eliminar una publicación de adopción
class PublicacionAdopcionDeleteView(generics.DestroyAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_object(self):
        id = self.kwargs.get("id")
        publicacion_adopcion = get_object_or_404(PublicacionAdopcion, id=id)
        if publicacion_adopcion.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar esta publicación de adopción"
            )
        return publicacion_adopcion

    def perform_destroy(self, instance):
        instance.delete()


## PUBLICACION DE ADOPCION - PARA LOS CLIENTES


class PublicacionAdopcionClienteView(generics.ListAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_queryset(self):
        email_fundacion = self.request.query_params.get("email_fundacion")
        user = get_object_or_404(User, email=email_fundacion)
        fundacion = get_object_or_404(Fundacion, user=user)
        return PublicacionAdopcion.objects.select_related("mascota").filter(
            fundacion=fundacion
        )


# --------------------------------------------------------------------------

# DETALLE MASCOTA - PARA PUBLICACIONES DE ADOPCION


class DetalleMascotaCreateView(generics.ListCreateAPIView):
    queryset = DetalleMascota.objects.all()
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = DetalleMascotaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Detalle de mascota agregado correctamente"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error en la crear el detalle de mascota",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DetalleMascotaView(generics.ListAPIView):
    serializer_class = DetalleMascotaSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_queryset(self):
        id_mascota = self.kwargs.get("id")
        mascota = get_object_or_404(Mascota, id=id_mascota)
        return DetalleMascota.objects.filter(mascota=mascota)


class DetalleMascotaUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_object(self, id):
        try:
            return DetalleMascota.objects.get(id=id)
        except DetalleMascota.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        detalle_mascota = self.get_object(id)
        if not detalle_mascota:
            return Response(
                {"message": "Detalle de mascota no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DetalleMascotaSerializer(detalle_mascota, data=request.data)

        if serializer.is_valid():
            serializer.update(detalle_mascota, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetalleMascotaDeleteView(generics.DestroyAPIView):
    serializer_class = DetalleMascotaSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_object(self):
        id = self.kwargs.get("id")
        detalle_mascota = get_object_or_404(DetalleMascota, id=id)
        return detalle_mascota

    def perform_destroy(self, instance):
        instance.delete()


## SOLICITUD DE ADOPCIÓN - DEL CLIENTE


class SolicitudAdopcionCreateView(generics.ListCreateAPIView):
    queryset = SolicitudAdopcion.objects.all()
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = SolicitudAdopcionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Solicitud de adopción enviada correctamente"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al enviar la solicitud de adopción",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SolicitudesAdopcionUserView(generics.ListAPIView):
    serializer_class = SolicitudAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return SolicitudAdopcion.objects.filter(user=user)


class SolicitudAdopcionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SolicitudAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(SolicitudAdopcion, id=id)
