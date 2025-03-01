import os
from django.shortcuts import render, redirect, get_object_or_404
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
from rest_framework import status
from django.utils.timezone import now
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .utils import generate_random_code
from datetime import timedelta
from django.utils import timezone
from django.test import RequestFactory

from django.contrib.auth.decorators import login_required


# from .forms import RegistroForm, ClienteCreationForm, FundacionCreationForm
from .models import *

# from .utils import send_code_to_user
from .new_utils import (
    send_code_to_user,
    send_test_email,
    send_update_adoption_email,
    send_update_care_email,
    send_cancel_care_email,
    send_create_care_email,
    money_format,
)
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

import mercadopago
import json


sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_ACCESS_TOKEN"))


@csrf_exempt
def create_preference_cuidado(request):
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        try:
            body = json.loads(request.body)

            user_id = body.get("user_id")
            mascota_id = body.get("mascota_id")
            cuidador_id = body.get("cuidador_id")
            total = body.get("total")

            if not user_id or not mascota_id or not cuidador_id or not total:
                return JsonResponse({"error": "Faltan datos obligatorios"}, status=400)

            preference_data = {
                "items": [
                    {
                        "title": "Servicio de Cuidado de Mascotas",
                        "quantity": 1,
                        "unit_price": float(total),
                        "currency_id": "COP",
                    }
                ],
                "payer": {
                    "email": body.get("email"),
                },
                "back_urls": {
                    "success": "https://makishop.live/cuidado/success",
                    "failure": "https://makishop.live/cuidado/failure",
                    "pending": "https://makishop.live/cuidado/pending",
                },
                "auto_return": "approved",
                "notification_url": "https://backend.makishop.live/api/mercadopago/webhook_cuidado/",
                "metadata": {
                    "user_id": str(user_id),
                    "mascota_id": str(mascota_id),
                    "cuidador_id": str(cuidador_id),
                },
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            return JsonResponse(
                {
                    "id": preference.get("id"),
                    "init_point": preference.get("init_point"),
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def mercadopago_webhook_cuidado(request):
    if request.method == "POST":
        try:
            raw_data = request.body.decode("utf-8")
            print(f"📩 Webhook recibido: {raw_data}")

            data = json.loads(raw_data)

            # Ignorar webhooks de merchant_order
            if data.get("topic") == "merchant_order":
                print("⚠️ Webhook de merchant_order recibido, ignorando...")
                return JsonResponse({"message": "Merchant order ignorado"}, status=200)

            # Verificar que es un evento de pago
            if data.get("type") != "payment":
                print("⚠️ Evento no relacionado con pagos, ignorando...")
                return JsonResponse(
                    {"message": "Evento no relacionado con pagos"}, status=200
                )

            # Obtener el ID del pago
            payment_id = data.get("data", {}).get("id", None)
            if not payment_id:
                print("❌ No se recibió un ID de pago válido")
                return JsonResponse(
                    {"error": "No se recibió un ID de pago"}, status=400
                )

            print(f"✔ ID de pago recibido: {payment_id}")

            # Consultar Mercado Pago usando el SDK correctamente
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)

            if (
                "response" not in payment_info
                or "status" not in payment_info["response"]
            ):
                print("❌ No se pudo obtener información del pago")
                return JsonResponse(
                    {"error": "No se pudo obtener información del pago"}, status=400
                )

            payment_status = payment_info["response"]["status"]
            metadata = payment_info["response"].get("metadata", {})

            print(f"🔹 Estado del pago: {payment_status}")
            print(f"🔹 Metadata recibida: {metadata}")

            # Validar si el pago fue aprobado
            if payment_status == "approved":
                user_id = metadata.get("user_id")
                email = metadata.get("email")
                mascota_id = metadata.get("mascota_id")
                cuidador_id = metadata.get("cuidador_id")
                fecha_inicio = metadata.get("fecha_inicio")
                fecha_fin = metadata.get("fecha_fin")
                horas_cuidado = metadata.get("horas_cuidado", 0)
                is_cuidado_especial = metadata.get("is_cuidado_especial", False)
                descripcion = metadata.get("descripcion", "No disponible")
                total = payment_info["response"]["transaction_amount"]

                # Validar la existencia de los registros en la base de datos
                try:
                    cliente = Cliente.objects.get(id=user_id)
                    mascota = Mascota.objects.get(id=mascota_id)
                    cuidador = Cuidador.objects.get(id=cuidador_id)
                except Cliente.DoesNotExist:
                    return JsonResponse({"error": "Cliente no encontrado"}, status=400)
                except Mascota.DoesNotExist:
                    return JsonResponse({"error": "Mascota no encontrada"}, status=400)
                except Cuidador.DoesNotExist:
                    return JsonResponse({"error": "Cuidador no encontrado"}, status=400)

                # Crear la solicitud de cuidado
                solicitud_data = {
                    "cliente": cliente.id,
                    "mascota": mascota.id,
                    "cuidador": cuidador.id,
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "horas_cuidado": horas_cuidado,
                    "is_cuidado_especial": is_cuidado_especial,
                    "descripcion": descripcion,
                    "estado": "Aceptada",
                    "costo": total,
                }

                serializer = SolicitudCuidadoSerializer(data=solicitud_data)
                if serializer.is_valid():
                    solicitud = serializer.save()
                    print(f"✅ Solicitud de cuidado creada con ID {solicitud.id}")
                    return JsonResponse(
                        {"message": "Solicitud creada exitosamente"}, status=201
                    )
                else:
                    print("❌ Error al serializar la solicitud", serializer.errors)
                    return JsonResponse({"error": serializer.errors}, status=400)

            return JsonResponse({"message": "Pago no aprobado"}, status=200)

        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return JsonResponse({"error": str(e)}, status=500)


# @csrf_exempt
# def mercadopago_webhook_cuidado(request):
#     if request.method == "POST":
#         try:
#             sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
#             raw_data = request.body.decode("utf-8")
#             print(f"📌 Webhook recibido: {raw_data}")

#             data = json.loads(raw_data)
#             payment_id = data.get("data", {}).get("id")
#             if not payment_id:
#                 print("⚠️ No se recibió un ID de pago válido")
#                 return JsonResponse({"error": "ID de pago no válido"}, status=400)

#             payment = sdk.payment().get(payment_id)
#             payment_status = payment["response"]["status"]
#             metadata = payment["response"].get("metadata", {})

#             user_id = metadata.get("user_id")
#             cliente = Cliente.objects.filter(
#                 user__id=user_id
#             ).first()  # 🔹 Buscar Cliente por User
#             if not cliente:
#                 print(f"⚠️ No se encontró un Cliente para el User ID {user_id}")
#                 return JsonResponse({"error": "Cliente no encontrado"}, status=400)

#             mascota_id = metadata.get("mascota_id")
#             if mascota_id is None:
#                 print("⚠️ `mascota_id` no está presente en metadata:", metadata)
#                 return JsonResponse(
#                     {"error": "mascota_id no encontrado en metadata"}, status=400
#                 )

#             cuidador_id = metadata.get("cuidador_id")

#             if not user_id or not mascota_id or not cuidador_id:
#                 print(
#                     f"⚠️ Error: Falta user_id ({user_id}), mascota_id ({mascota_id}), o cuidador_id ({cuidador_id}) en metadata."
#                 )
#                 return JsonResponse({"error": "Faltan datos en metadata"}, status=400)

#             total = payment["response"]["transaction_amount"]

#             if payment_status == "approved":
#                 print(f"✔ Creando solicitud de cuidado para User {user_id}")

#                 factory = RequestFactory()

#                 # Buscar el Cliente asociado al User ID
#                 cliente = Cliente.objects.filter(user__id=user_id).first()

#                 if not cliente:
#                     print(f"⚠️ No se encontró un Cliente para el User ID {user_id}")
#                     return JsonResponse({"error": "Cliente no encontrado"}, status=400)

#                 request_data = {
#                     "email": "usuario@example.com",  # 🔹 Reemplazar con email válido si está disponible
#                     "id_cliente": cliente.id,  # 🔹 Enviar el ID correcto del Cliente
#                     "id_mascota": mascota_id,
#                     "id_cuidador": cuidador_id,
#                     "fecha_solicitud": timezone.now().isoformat(),
#                     "fecha_inicio": timezone.now().isoformat(),
#                     "fecha_fin": timezone.now().isoformat(),
#                     "horas_cuidado": 0,
#                     "is_cuidado_especial": False,
#                     "descripcion": "Pago aprobado en Mercado Pago.",
#                     "costo": total,
#                     "estado": "Pendiente",
#                 }

#                 print(f"📌 Enviando datos a la API: {request_data}")

#                 request_fake = factory.post(
#                     "/solicitud-cuidado/create/",
#                     data=json.dumps(request_data),
#                     content_type="application/json",
#                 )

#                 response = SolicitudCuidadoCreateView.as_view()(request_fake)

#                 if response.status_code == status.HTTP_201_CREATED:
#                     print("✅ Solicitud creada exitosamente")
#                     return JsonResponse(
#                         {"message": "Solicitud de cuidado creada exitosamente."},
#                         status=201,
#                     )
#                 else:
#                     print(f"⚠ Error en la creación de solicitud: {response.data}")
#                     return JsonResponse({"error": response.data}, status=400)

#             return JsonResponse({"message": "Pago no aprobado"}, status=200)

#         except Exception as e:
#             print(f"⚠️ Error inesperado en el Webhook: {str(e)}")
#             return JsonResponse({"error": str(e)}, status=500)

#     return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def create_membership_preference(request):
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        try:
            body = json.loads(request.body)

            user_id = body.get("user_id")
            if not user_id:
                return JsonResponse({"error": "user_id es obligatorio"}, status=400)

            # Obtener el usuario para verificar si es fundación
            try:
                user = User.objects.get(id=user_id)
                if not user.is_fundacion:
                    return JsonResponse(
                        {"error": "Solo las fundaciones pueden comprar membresías"},
                        status=403,
                    )
            except User.DoesNotExist:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            # Configuración del plan de membresía
            membership_plan = body.get("membership_plan")  # Puede ser 'Peludos' u otro
            price = 26000  # Precio fijo en COP para la membresía "Peludos"

            preference_data = {
                "items": [
                    {
                        "title": f"Membresía {membership_plan}",
                        "quantity": 1,
                        "unit_price": price,
                        "currency_id": "COP",
                    }
                ],
                "back_urls": {
                    "success": "https://makishop.live/membresias/success",
                    "failure": "https://makishop.live/membresias/failure",
                    "pending": "https://makishop.live/membresias/pending",
                },
                "auto_return": "approved",
                "notification_url": "https://backend.makishop.live/api/mercadopago/membership-webhook/",
                "metadata": {
                    "user_id": str(user_id),
                    "membership_plan": membership_plan,
                },
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            return JsonResponse(
                {
                    "id": preference.get("id"),
                    "init_point": preference.get("init_point"),
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def membership_webhook(request):
    if request.method == "POST":
        try:
            raw_data = request.body.decode("utf-8")
            print(f"🔹 Webhook recibido: {raw_data}")

            data = json.loads(raw_data)

            if data.get("topic") == "merchant_order":
                print("⚠️ Webhook de merchant_order recibido, ignorando...")
                return JsonResponse({"message": "Merchant order ignorado"}, status=200)

            payment_id = data.get("data", {}).get("id", None)
            if not payment_id:
                print("❌ No se recibió un ID de pago válido")
                return JsonResponse(
                    {"error": "No se recibió un ID de pago"}, status=400
                )

            print(f"✔ ID de pago recibido: {payment_id}")

            # Consultar el pago en Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            payment = sdk.payment().get(payment_id)
            payment_status = payment["response"]["status"]
            user_id = payment["response"].get("metadata", {}).get("user_id", None)

            print(f"🔹 Estado del pago: {payment_status}")
            print(f"🔹 ID de usuario en metadata: {user_id}")

            if not user_id:
                print("❌ No se encontró user_id en metadata")
                return JsonResponse(
                    {"error": "Usuario no encontrado en metadata"}, status=400
                )

            # Validar si el pago fue aprobado
            if payment_status == "approved":
                try:
                    user = User.objects.get(id=user_id)
                    fundacion = Fundacion.objects.get(user=user)
                    fundacion.premium = True
                    fundacion.save()
                    print(
                        f"✅ Membresía activada para la fundación: {fundacion.nombre}"
                    )
                    return JsonResponse(
                        {"message": "Membresía activada exitosamente"}, status=200
                    )
                except User.DoesNotExist:
                    print(f"❌ No se encontró usuario con ID {user_id}")
                    return JsonResponse({"error": "Usuario no encontrado"}, status=404)
                except Fundacion.DoesNotExist:
                    print(
                        f"❌ No se encontró fundación asociada al usuario {user.email}"
                    )
                    return JsonResponse(
                        {"error": "Fundación no encontrada"}, status=404
                    )

            print("⚠️ El pago no fue aprobado, no se activa la membresía.")
            return JsonResponse({"message": "Pago no aprobado"}, status=200)

        except json.JSONDecodeError:
            print("❌ Error al decodificar JSON")
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def create_preference(request):
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        try:
            body = json.loads(request.body)

            # Verificar si `user_id` viene en la solicitud
            user_id = body.get("user_id")
            if not user_id:
                print("No se envió user_id en la solicitud")
                return JsonResponse({"error": "user_id es obligatorio"}, status=400)

            print(f"User ID recibido: {user_id}")

            preference_data = {
                "items": body["items"],
                "back_urls": {
                    "success": "https://makishop.live/",
                    "failure": "https://makishop.live/failure",
                    "pending": "https://makishop.live/pending",
                },
                "auto_return": "approved",
                "notification_url": "https://backend.makishop.live/api/mercadopago/webhook/",
                "metadata": {
                    "user_id": str(
                        user_id
                    )  # Convertir `user_id` a string por compatibilidad
                },
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]

            print(f"Preferencia creada con metadata: {preference_data['metadata']}")

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
            raw_data = request.body.decode("utf-8")
            print(f"Webhook recibido: {raw_data}")

            data = json.loads(raw_data)
            print(f"Datos parseados: {data}")

            # IGNORAR LOS WEBHOOKS DE merchant_order
            if data.get("topic") == "merchant_order":
                print("Webhook de merchant_order recibido, ignorando...")
                return JsonResponse({"message": "Merchant order ignorado"}, status=200)

            # PROCESAR SOLO PAYMENT.CREATED
            payment_id = data.get("data", {}).get("id", None)
            if not payment_id:
                print("No se recibió un ID de pago válido")
                return JsonResponse(
                    {"error": "No se recibió un ID de pago"}, status=400
                )

            print(f"✔ ID de pago recibido: {payment_id}")

            # Consultar el pago en Mercado Pago
            payment = sdk.payment().get(payment_id)
            payment_status = payment["response"]["status"]
            user_id = payment["response"].get("metadata", {}).get("user_id", None)

            print(f"Estado del pago: {payment_status}")
            print(f"ID de usuario recibido en metadata: {user_id}")

            if not user_id:
                print("No se encontró user_id en metadata")
                return JsonResponse(
                    {"error": "Usuario no encontrado en metadata"}, status=400
                )

            # Buscar al usuario en la base de datos
            try:
                user = User.objects.get(id=user_id)
                print(f"Usuario encontrado en la base de datos: {user.email}")
            except User.DoesNotExist:
                print(f"No se encontró usuario con ID {user_id}")
                return JsonResponse({"error": "Usuario no encontrado"}, status=400)

            # Obtener el carrito del usuario más reciente
            carrito = (
                Carrito.objects.filter(user=user, pagado=False).order_by("-id").first()
            )

            if not carrito:
                print(f"No se encontró carrito activo para el usuario: {user.email}")
                return JsonResponse({"error": "Carrito no encontrado"}, status=400)

            if payment_status == "approved":
                # Verificar si el carrito tiene productos
                items_en_carrito = list(
                    carrito.items.all()
                )  # Convertir a lista para debug
                print(f"Items en carrito: {items_en_carrito}")

                if not carrito.items.exists():
                    print(f"El carrito del usuario {user.email} está vacío")
                    return JsonResponse(
                        {"error": "El carrito estaba vacío, no se creó el pedido"},
                        status=400,
                    )

                # Crear el pedido solo si hay productos en el carrito
                nuevo_pedido = Pedido.objects.create(
                    user=user,
                    total=sum(
                        item.producto.precio * item.cantidad
                        for item in items_en_carrito
                    ),
                    estado="Preparación",
                )
                print(
                    f"Pedido {nuevo_pedido.id} creado con total: {nuevo_pedido.total}"
                )

                # Transferir productos al pedido y reducir stock
                for item in items_en_carrito:
                    DetallePedido.objects.create(
                        pedido=nuevo_pedido,
                        producto=item.producto,
                        cantidad=item.cantidad,
                    )
                    print(f"Producto {item.producto.nombre} agregado al pedido")

                    # **Reducir stock del producto**
                    if item.producto.stock >= item.cantidad:
                        item.producto.stock -= item.cantidad
                        item.producto.save()
                        print(
                            f"Stock actualizado: {item.producto.nombre} - {item.producto.stock} unidades restantes"
                        )
                    else:
                        print(f"⚠️ Stock insuficiente para {item.producto.nombre}")

                # Marcar el carrito como pagado
                carrito.pagado = True
                carrito.save()
                print(f"Carrito {carrito.codigo} marcado como pagado.")

                return JsonResponse(
                    {
                        "message": "Pago aprobado, pedido creado y stock actualizado",
                        "reset_cart": True,
                    },
                    status=201,
                )

            return JsonResponse({"message": "Pago no aprobado"}, status=200)

        except json.JSONDecodeError:
            print("Error al decodificar JSON")
            return JsonResponse({"error": "JSON inválido"}, status=400)
        except Exception as e:
            print(f"Error inesperado: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


from django.db import transaction


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pagar_con_saldo_maki(request):
    try:
        user = request.user
        codigo_carrito = request.data.get("codigo_carrito")

        carrito = get_object_or_404(
            Carrito, codigo=codigo_carrito, user=user, pagado=False
        )
        total_pedido = sum(
            item.producto.precio * item.cantidad for item in carrito.items.all()
        )

        if user.saldo < total_pedido:
            return Response({"error": "Saldo insuficiente"}, status=400)

        with transaction.atomic():
            user.saldo -= total_pedido
            user.save()

            pedido = Pedido.objects.create(
                user=user, total=total_pedido, estado="Preparación"
            )
            for item in carrito.items.all():
                DetallePedido.objects.create(
                    pedido=pedido, producto=item.producto, cantidad=item.cantidad
                )
                item.producto.stock -= item.cantidad
                item.producto.save()

            carrito.pagado = True
            carrito.save()

        return Response(
            {"message": "Pedido realizado con éxito usando saldo de Maki"}, status=200
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def SendTestEmail(request):
    try:
        response = send_test_email()
        return Response({"message": response["message"]})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class ClienteSignupView(generics.ListCreateAPIView):
#     # serializer_class = ClienteSignupSerializer
#     # def post(self, request, *args, **kwargs):
#     #     serializer = self.get_serializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     user = serializer.save()
#     #     return Response({
#     #             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#     #             "token": Token.objects.get(user=user).key,
#     #             "message": "Cliente creado exitosamente",
#     #         })
#     queryset = Cliente.objects.all()
#     serializer_class = ClienteSignupSerializer
#     permission_classes = [permissions.AllowAny]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             send_code_to_user(user.email)
#             # if sendgrid_response.status_code != 200:
#             #     user.delete()
#             #     return Response(
#             #         {
#             #             "error": sendgrid_response.text,
#             #             "detail": "Ha ocurrido un error en el envió de tu correo de confirmación. Comunicamente con soporte técnico.",
#             #         },
#             #         status=status.HTTP_201_CREATED,
#             #     )
#             return Response(
#                 {
#                     "user": UserSerializer(
#                         user, context=self.get_serializer_context()
#                     ).data,
#                     "message": "Cliente creado exitosamente. Se envió un código de verificación a tu correo electrónico",
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         errores = {}
#         print(serializer.errors)
#         for key, value in serializer.errors.items():
#             errores[key] = ", ".join(value)

#         mensaje = " | ".join([f"{key}: {value}" for key, value in errores.items()])
#         return Response(
#             {
#                 "error": serializer.errors,
#                 "detail": mensaje,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class ClienteSignupView(generics.ListCreateAPIView):

    queryset = User.objects.all()  # Asegúrate de usar el modelo correcto de usuario
    serializer_class = ClienteSignupSerializer  # Usamos el serializer para clientes
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Aquí se está usando el serializer de cliente
        serializer = self.get_serializer(data=request.data)

        # Verificar si el serializer es válido
        if serializer.is_valid():
            # Guardar el nuevo usuario (cliente)
            user = serializer.save()

            # Enviar el código de verificación por correo
            send_code_to_user(user.email)

            # Responder con un mensaje de éxito
            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "message": "Cliente creado exitosamente. Se envió un código de verificación a tu correo electrónico",
                },
                status=status.HTTP_201_CREATED,
            )

        # Si los datos del serializer no son válidos, se devuelven los errores
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

            first_login = user.last_login is None  # Verificar si es la primera vez
            user.last_login = now()
            user.save(update_fields=["last_login"])

            data = {}
            refresh = self.get_token(user)
            data["id"] = user.id  # Enviar `user_id`
            data["email"] = user.email
            data["is_cliente"] = user.is_cliente
            data["is_fundacion"] = user.is_fundacion
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)
            data["last_login"] = user.last_login
            data["first_login"] = first_login

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
            return Response(
                {
                    "message": "Fundación actualizada exitosamente",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "error": serializer.errors,
                "detail": "Ha ocurrido un error al actualizar la fundación",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


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
        return Fundacion.objects.select_related("user").filter(user__is_verified=True)


class FundacionLocalidadView(generics.ListAPIView):
    serializer_class = FundacionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        id_localidad = self.kwargs.get("id")
        localidad = get_object_or_404(Localidad, id=id_localidad)
        return Fundacion.objects.select_related("user__direccion__localidad").filter(
            user__direccion__localidad=localidad, user__is_verified=True
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
        mascotas = Mascota.objects.filter(user=user)
        # Debug: Imprimir los datos antes de enviarlos
        # print("Datos de mascotas enviados al frontend:")
        # for mascota in mascotas:
        #     print(
        #         {
        #             "id": mascota.id,
        #             "nombre": mascota.nombre,
        #             "sexo": mascota.sexo,
        #             "tipo": mascota.tipo,
        #             "raza": mascota.raza,
        #             "edad": mascota.edad,
        #             "estado_salud": mascota.estado_salud,
        #             "tamano": mascota.tamano,
        #             "peso": mascota.peso,
        #             "imagen": (
        #                 mascota.imagen.url if mascota.imagen else "No tiene imagen"
        #             ),
        #         }
        #     )

        return mascotas


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
        user_id = request.data.get("user_id")  # Asegurar que user_id se reciba

        # Verifica si los datos son válidos
        if not codigo or not id_producto or not user_id:
            return JsonResponse(
                {
                    "error": "Faltan datos obligatorios: 'codigo', 'id_producto' o 'user_id'"
                },
                status=400,
            )

        user = User.objects.get(id=user_id)

        carrito, creado = Carrito.objects.get_or_create(
            codigo=codigo, defaults={"user": user}
        )

        # Si el carrito ya existe y no tiene user_id, lo asignamos
        if not carrito.user:
            carrito.user = user
            carrito.save()

        producto = Producto.objects.get(id=id_producto)

        item_carrito, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito, producto=producto
        )
        item_carrito.cantidad += 1
        item_carrito.save()

        serializer = ItemCarritoSerializer(item_carrito)
        return JsonResponse(
            {
                "data": serializer.data,
                "message": "Producto agregado al carrito exitosamente",
            },
            status=201,
        )

    except User.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=400)
    except Exception as e:
        print("Error en el servidor:", str(e))
        return JsonResponse({"error": str(e)}, status=500)


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


@api_view(["POST"])
def crear_carrito(request):
    try:
        data = request.data
        codigo = data.get("codigo")
        user_id = data.get("user_id")

        if not codigo:
            return Response({"error": "Código de carrito es obligatorio"}, status=400)

        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                print("Usuario no encontrado, creando carrito sin usuario.")

        nuevo_carrito = Carrito.objects.create(codigo=codigo, user=user)
        print(f"✅ Nuevo carrito creado: {nuevo_carrito.codigo}")

        return Response(
            {"message": "Carrito creado exitosamente", "codigo": nuevo_carrito.codigo},
            status=201,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


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

    try:
        carrito = get_object_or_404(Carrito, codigo=codigo_carrito)
    except Carrito.DoesNotExist:
        print(f"No se encontró carrito con código: {codigo_carrito}")
        return Response({"error": "Carrito no encontrado."}, status=404)

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


# class ResenaCreateView(generics.ListCreateAPIView):
#     queryset = Resena.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = ResenaSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"message": "Reseña creada exitosamente"},
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(
#             {
#                 "error": serializer.errors,
#                 "message": "Ha ocurrido un error al crear la reseña",
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class ResenaProductoCreateView(generics.ListCreateAPIView):
    queryset = Resena.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ResenaSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        producto_id = data.get("id")

        if not producto_id:
            return Response(
                {
                    "error": "Falta el ID del producto",
                    "detail": "Ha ocurrido un error al crear la reseña. Falta el ID del producto.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content_type = ContentType.objects.get_for_model(Producto)
        except ContentType.DoesNotExist:
            return Response(
                {
                    "error": "El modelo 'producto' no es válido",
                    "detail": "Ha ocurrido un error al crear la reseña. Producto no es válido.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data["content_type"] = content_type.id
        data["object_id"] = producto_id

        email = data.get("email")
        user = get_object_or_404(User, email=email)

        if Resena.objects.filter(
            content_type=content_type, object_id=producto_id, user=user
        ).exists():
            return Response(
                {
                    "error": "Ya has creado una reseña para este producto",
                    "detail": "No puedes crear más de una reseña para este producto.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Reseña de producto creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": serializer.errors,
                "detail": "Ha ocurrido un error al crear la reseña",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResenaCuidadorCreateView(generics.ListCreateAPIView):
    queryset = Resena.objects.all()
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = ResenaSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        cuidador_id = data.get("id")

        if not cuidador_id:
            return Response(
                {
                    "error": "Falta el ID del cuidador",
                    "detail": "Ha ocurrido un error al crear la reseña. Falta el ID del cuidador.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            content_type = ContentType.objects.get_for_model(Cuidador)
        except ContentType.DoesNotExist:
            return Response(
                {
                    "error": "El modelo 'cuidador' no es válido",
                    "detail": "Ha ocurrido un error al crear la reseña. Cuidador no es válido.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data["content_type"] = content_type.id
        data["object_id"] = cuidador_id

        email = data.get("email")
        user = get_object_or_404(User, email=email)

        if Resena.objects.filter(
            content_type=content_type, object_id=cuidador_id, user=user
        ).exists():
            return Response(
                {
                    "error": "Ya has creado una reseña para este cuidador",
                    "detail": "No puedes crear más de una reseña para este cuidador.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Reseña de cuidador creada exitosamente"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": serializer.errors,
                "detail": "Ha ocurrido un error al crear la reseña",
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
        producto_id = self.kwargs["id"]
        content_type = ContentType.objects.get_for_model(Producto)
        return Resena.objects.filter(content_type=content_type, object_id=producto_id)


class ResenaCuidadorView(generics.ListAPIView):
    serializer_class = ResenaSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_queryset(self):
        cuidador_id = self.kwargs["id"]
        content_type = ContentType.objects.get_for_model(Cuidador)
        return Resena.objects.filter(content_type=content_type, object_id=cuidador_id)


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
@api_view(["PUT"])
def cancelar_pedido(request, pedido_id):
    print(f"Intentando cancelar pedido con ID: {pedido_id}")

    user = request.user
    print(f"Usuario autenticado: {user}")

    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        print(f"Pedido encontrado: {pedido}")

        if pedido.user != user:
            return Response(
                {
                    "error": "No tienes permisos para cancelar este pedido",
                    "detail": "No tienes permisos para cancelar este pedido",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if pedido.estado in ["Cancelado", "Entregado", "Transito"]:
            return Response(
                {
                    "error": "Este pedido no puede ser cancelado.",
                    "detail": "Este pedido no puede ser cancelado.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            pedido.estado = "Cancelado"
            pedido.save()
            print("Pedido cancelado con éxito")

            # Verificar límite antes de actualizar saldo
            nuevo_saldo = user.saldo + pedido.total
            if nuevo_saldo > 999999999.99:  # Límite del DecimalField
                return Response(
                    {
                        "error": "No se puede actualizar el saldo: excede el límite permitido.",
                        "detail": "No se puede actualizar el saldo: excede el límite permitido.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.saldo = nuevo_saldo
            user.save()
            print(f"Saldo actualizado: {user.saldo}")

            return Response(
                {"message": "Pedido cancelado y saldo reembolsado correctamente."},
                status=status.HTTP_200_OK,
            )

    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return Response(
            {"error": f"Ocurrió un error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
                "detail": "Ha ocurrido un error al crear el pedido",
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
                "detail": "Ha ocurrido un error al crear el detalle de pedido",
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
            publicacion = serializer.save()
            publicacion_data = self.get_serializer(publicacion).data
            return Response(
                {
                    "publicacion": publicacion_data,
                    "message": "Publicación de adopción creada exitosamente",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "error": serializer.errors,
                "detail": "Ha ocurrido un error al crear la publicación de adopción",
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
        fundacion = get_object_or_404(Fundacion, user=user)
        return PublicacionAdopcion.objects.filter(fundacion=fundacion)


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
    serializer_class = PublicacionAdopcionSerializer
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
        if publicacion_adopcion.fundacion.user != self.request.user:
            raise exceptions.PermissionDenied(
                "No tienes permisos para eliminar esta publicación de adopción"
            )
        return publicacion_adopcion

    def perform_destroy(self, instance):
        detalle_asociado = DetalleMascota.objects.filter(mascota=instance.mascota)
        if detalle_asociado:
            detalle_asociado.delete()
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


## PUBLICACION DE ADOPCION - PARA LAS FUNDACIONES
class PublicacionAdopcionFundacionView(generics.ListAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        fundacion = get_object_or_404(Fundacion, user=user)
        return PublicacionAdopcion.objects.select_related("mascota").filter(
            fundacion=fundacion
        )


## PUBLICACION DE ADOPCION - PARA LAS FUNDACIONES
class PublicacionAdopcionFundacionView(generics.ListAPIView):
    serializer_class = PublicacionAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
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
                "detail": "Ha ocurrido un error en la crear el detalle de mascota",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# Cuidadores
class ListaCuidadoresView(APIView):
    serializer_class = CuidadorSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get(self, request):
        cuidadores = Cuidador.objects.all()
        serializer = CuidadorSerializer(cuidadores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CuidadorDetailView(APIView):
    serializer_class = CuidadorSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(Cuidador, id=id)

    def get(self, request, id):
        cuidador = self.get_object()
        serializer = CuidadorSerializer(cuidador)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Detalle Mascotas
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


# --------------------------------------------------------------------------

## SOLICITUD DE ADOPCIÓN - DEL CLIENTEda


class SolicitudAdopcionCreateView(generics.ListCreateAPIView):
    queryset = SolicitudAdopcion.objects.all()
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = SolicitudAdopcionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Solicitud de adopción enviada correctamente. Debes esperar a la respuesta de la fundación."
                },
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
        return SolicitudAdopcion.objects.filter(cliente__user=user)


class SolicitudAdopcionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SolicitudAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(SolicitudAdopcion, id=id)


## SOLICITUD DE ADOPCION - PARA LA FUNDACIÓN
class SolicitudesAdopcionFundacionView(generics.ListAPIView):
    serializer_class = SolicitudAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return SolicitudAdopcion.objects.filter(publicacion__fundacion__user=user)


class SolicitudAdopcionFunDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SolicitudAdopcionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(SolicitudAdopcion, id=id)


class SolicitudAdopcionUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = SolicitudAdopcionSerializer

    def get_object(self, id):
        try:
            return SolicitudAdopcion.objects.get(id=id)
        except SolicitudAdopcion.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        solicitud_adopcion = self.get_object(id)
        if not solicitud_adopcion:
            return Response(
                {"message": "Solicitud de adopción no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if solicitud_adopcion.publicacion.fundacion.user != request.user:
            raise PermissionDenied(
                "No tienes permisos para editar esta solicitud de adopción"
            )
        serializer = SolicitudAdopcionSerializer(solicitud_adopcion, data=request.data)
        if serializer.is_valid():
            serializer.update(solicitud_adopcion, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActualizarEstadoSolicitudAdopcion(APIView):
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]
    serializer_class = SetEstadoSolicitudAdopcionSerializer

    def get_object(self, id):
        try:
            return SolicitudAdopcion.objects.get(id=id)
        except SolicitudAdopcion.DoesNotExist:
            return None

    def patch(self, request, id, *args, **kwargs):
        solicitud_adopcion = self.get_object(id)
        if not solicitud_adopcion:
            return Response(
                {"message": "Solicitud de adopción no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if solicitud_adopcion.publicacion.fundacion.user != request.user:
            raise PermissionDenied(
                "No tienes permisos para editar esta solicitud de adopción"
            )
        serializer = SetEstadoSolicitudAdopcionSerializer(
            solicitud_adopcion, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.update(solicitud_adopcion, serializer.validated_data)
            numero_solicitud = solicitud_adopcion.id
            email = solicitud_adopcion.cliente.user.email
            fecha = solicitud_adopcion.fecha
            nuevo_estado = solicitud_adopcion.estado
            nombre_mascota = solicitud_adopcion.publicacion.mascota.nombre
            sexo_mascota = solicitud_adopcion.publicacion.mascota.sexo
            tipo_mascota = solicitud_adopcion.publicacion.mascota.tipo
            raza_mascota = solicitud_adopcion.publicacion.mascota.raza
            edad_mascota = solicitud_adopcion.publicacion.mascota.edad
            motivo = solicitud_adopcion.motivo
            id_publicacion = solicitud_adopcion.publicacion.id
            nombre_fundacion = solicitud_adopcion.publicacion.fundacion.nombre
            telefono_fundacion = solicitud_adopcion.publicacion.fundacion.user.telefono
            direccion_fundacion = (
                solicitud_adopcion.publicacion.fundacion.user.direccion.direccion
            )
            localidad_fundacion = (
                solicitud_adopcion.publicacion.fundacion.user.direccion.localidad.nombre
            )
            email_fundacion = solicitud_adopcion.publicacion.fundacion.user.email

            send_update_adoption_email(
                numero_solicitud,
                email,
                fecha,
                nuevo_estado,
                nombre_mascota,
                sexo_mascota,
                tipo_mascota,
                raza_mascota,
                edad_mascota,
                motivo,
                id_publicacion,
                nombre_fundacion,
                telefono_fundacion,
                direccion_fundacion,
                localidad_fundacion,
                email_fundacion,
            )
            return Response(serializer.data)
        return Response(
            {
                "error": serializer.errors,
                "detail": "Ha ocurrido un error al actualizar el estado de la solicitud de adopción",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


## CATEGORIAS DE PRODUCTOS


class SubcategoriasDeCategoriaView(generics.ListAPIView):
    serializer_class = SubcategoriaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        nombre_categoria = self.kwargs.get("nombre")
        categoria = get_object_or_404(Categoria, nombre=nombre_categoria)
        return Subcategoria.objects.filter(categoria=categoria)


class ProductosPorCategoriasView(generics.ListAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        categoria_principal = self.request.query_params.get("categoria_principal", None)
        categoria = self.request.query_params.get("categoria", None)
        sub_categoria = self.request.query_params.get("sub_categoria", None)

        productos = Producto.objects.all()
        print(categoria_principal, categoria, sub_categoria)
        if categoria_principal and categoria == None and sub_categoria == None:
            productos_ids = ProductoCategorias.objects.filter(
                sub_categoria__categoria__categoria_principal__nombre=categoria_principal
            ).values_list("producto", flat=True)
            print(productos_ids)
            productos = productos.filter(id__in=productos_ids)
            print(productos)
        elif categoria_principal and categoria and sub_categoria == None:
            productos_ids = ProductoCategorias.objects.filter(
                sub_categoria__categoria__nombre=categoria,
                sub_categoria__categoria__categoria_principal__nombre=categoria_principal,
            ).values_list("producto", flat=True)
            productos = productos.filter(id__in=productos_ids)
        elif categoria_principal and categoria and sub_categoria:
            productos_ids = ProductoCategorias.objects.filter(
                sub_categoria__nombre=sub_categoria,
                sub_categoria__categoria__nombre=categoria,
                sub_categoria__categoria__categoria_principal__nombre=categoria_principal,
            ).values_list("producto", flat=True)
            productos = productos.filter(id__in=productos_ids)
        elif categoria and sub_categoria == None and categoria_principal == None:
            productos_ids = ProductoCategorias.objects.filter(
                sub_categoria__categoria__nombre=categoria
            ).values_list("producto", flat=True)
            productos = productos.filter(id__in=productos_ids)
        elif sub_categoria and categoria == None and categoria_principal == None:
            productos_ids = ProductoCategorias.objects.filter(
                sub_categoria__nombre=sub_categoria
            ).values_list("producto", flat=True)
            productos = productos.filter(id__in=productos_ids)

        return productos


## ORDENAMIENTO DE PRODUCTOS POR PRECIO


class OrdenarProductosPorPrecioAscView(generics.ListAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Producto.objects.all().order_by("precio")


class OrdenarProductosPorPrecioDescView(generics.ListAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Producto.objects.all().order_by("-precio")


# SOLICITUD DE CUIDADO


class SolictudCuidadoCreateView(generics.ListCreateAPIView):
    queryset = SolicitudCuidado.objects.all()
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = SolicitudCuidadoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Solicitud de cuidado enviada correctamente. Debes esperar a la respuesta del cuidador."
                },
                status=status.HTTP_201_CREATED,
            )
        print("Errores del serializador:", serializer.errors)
        return Response(
            {
                "error": serializer.errors,
                "message": "Ha ocurrido un error al enviar la solicitud de cuidado",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SolicitudCiudadoUserView(generics.ListAPIView):
    serializer_class = SolicitudCuidadoSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return SolicitudCuidado.objects.filter(cliente__user=user)


class SolicitudCuidadoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SolicitudCuidadoSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(SolicitudCuidado, id=id)


class SolicitudCuidadoUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = SolicitudCuidadoSerializer

    def get_object(self, id):
        try:
            return SolicitudCuidado.objects.get(id=id)
        except SolicitudCuidado.DoesNotExist:
            return None

    def put(self, request, id, *args, **kwargs):
        solicitud_cuidado = self.get_object(id)
        if not solicitud_cuidado:
            return Response(
                {"message": "Solicitud de cuidado no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if solicitud_cuidado.cliente.user != request.user:
            raise PermissionDenied(
                "No tienes permisos para editar esta solicitud de cuidado"
            )
        serializer = SolicitudCuidadoSerializer(solicitud_cuidado, data=request.data)
        if serializer.is_valid():
            serializer.update(solicitud_cuidado, serializer.validated_data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActualizarEstadoSolicitudCuidado(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SetEstadoSolicitudCuidadoSerializer

    def get_object(self, id):
        try:
            return SolicitudCuidado.objects.get(id=id)
        except SolicitudCuidado.DoesNotExist:
            return None

    def patch(self, request, id, *args, **kwargs):
        solicitud_cuidado = self.get_object(id)
        if not solicitud_cuidado:
            return Response(
                {"message": "Solicitud de cuidado no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if solicitud_cuidado.cuidador.user != request.user:
            raise PermissionDenied(
                "No tienes permisos para editar esta solicitud de cuidado"
            )
        serializer = SetEstadoSolicitudCuidadoSerializer(
            solicitud_cuidado, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.update(solicitud_cuidado, serializer.validated_data)
            numero_solicitud = solicitud_cuidado.id
            email = solicitud_cuidado.cliente.user.email
            fecha = solicitud_cuidado.fecha
            nuevo_estado = solicitud_cuidado.estado
            nombre_mascota = solicitud_cuidado.mascota.nombre
            sexo_mascota = solicitud_cuidado.mascota.sexo
            tipo_mascota = solicitud_cuidado.mascota.tipo
            raza_mascota = solicitud_cuidado.mascota.raza
            edad_mascota = solicitud_cuidado.mascota.edad
            descripcion = solicitud_cuidado.descripcion
            id_mascota = solicitud_cuidado.mascota.id
            nombre_cuidador = solicitud_cuidado.cuidador.nombre
            telefono_cuidador = solicitud_cuidado.cuidador.user.telefono
            direccion_cuidador = solicitud_cuidado.cuidador.direccion.direccion
            localidad_cuidador = solicitud_cuidado.cuidador.direccion.localidad.nombre
            email_cuidador = solicitud_cuidado.cuidador.user.email

            send_update_care_email(
                numero_solicitud,
                email,
                fecha,
                nuevo_estado,
                nombre_mascota,
                sexo_mascota,
                tipo_mascota,
                raza_mascota,
                edad_mascota,
                descripcion,
                id_mascota,
                nombre_cuidador,
                telefono_cuidador,
                direccion_cuidador,
                localidad_cuidador,
                email_cuidador,
            )

            return Response(serializer.data)
        return Response(
            {
                "error": serializer.errors,
                "detail": "Ha ocurrido un error al actualizar el estado de la solicitud de cuidado",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CancelarSolicitudCuidado(APIView):
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]
    serializer_class = SetEstadoSolicitudCuidadoSerializer

    def get_object(self, id):
        try:
            return SolicitudCuidado.objects.get(id=id)
        except SolicitudCuidado.DoesNotExist:
            return None

    def patch(self, request, id, *args, **kwargs):
        solicitud_cuidado = self.get_object(id)
        if not solicitud_cuidado:
            return Response(
                {
                    "error": "Solicitud de cuidado no encontrada",
                    "detail": "Solicitud de cuidado no encontrada",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if solicitud_cuidado.cliente.user != request.user:
            raise PermissionDenied(
                {
                    "error": "No tienes permisos para editar esta solicitud de cuidado",
                    "detail": "No tienes permisos para editar esta solicitud de cuidado",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if solicitud_cuidado.estado == "Cancelada":
            return Response(
                {
                    "error": "Esta solicitud ya ha sido cancelada",
                    "detail": "Esta solicitud ya ha sido cancelada",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        tiempo_restante = solicitud_cuidado.fecha_inicio - timezone.now()
        reembolso = 0

        # Reembolso segun los casos
        if tiempo_restante > timedelta(hours=48):
            reembolso = solicitud_cuidado.costo
        elif timedelta(hours=24) < tiempo_restante <= timedelta(hours=48):
            reembolso = solicitud_cuidado.costo * 0.5
        else:
            reembolso = 0

        # Actualización del saldo del cliente
        cliente = solicitud_cuidado.cliente
        try:
            cliente.user.saldo += reembolso
            cliente.save()
        except Exception as e:
            return Response(
                {
                    "error": "Ha ocurrido un error al actualizar el saldo del cliente",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Cambio en el estado de la solicitud
        solicitud_cuidado.estado = "Cancelada"
        solicitud_cuidado.fecha_actualizacion = timezone.now()
        solicitud_cuidado.save()

        # Envio de correo de cancelación
        numero_solicitud = solicitud_cuidado.id
        email = solicitud_cuidado.cliente.user.email
        fecha_solicitud = solicitud_cuidado.fecha_solicitud
        fecha_inicio = solicitud_cuidado.fecha_inicio
        fecha_actualizacion = solicitud_cuidado.fecha_actualizacion
        nombre_mascota = solicitud_cuidado.mascota.nombre
        descripcion = solicitud_cuidado.descripcion
        costo = money_format(solicitud_cuidado.costo)
        nombre_cuidador = f"{solicitud_cuidado.cuidador.primer_nombre} {solicitud_cuidado.cuidador.segundo_nombre or ''} {solicitud_cuidado.cuidador.primer_apellido} {solicitud_cuidado.cuidador.segundo_apellido or ''}"

        try:
            send_cancel_care_email(
                numero_solicitud,
                email,
                fecha_solicitud,
                fecha_inicio,
                fecha_actualizacion,
                nombre_mascota,
                descripcion,
                costo,
                nombre_cuidador,
            )
        except Exception as e:
            return Response(
                {
                    "error": "Ha ocurrido un error al enviar el correo de cancelación",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "message": "Solicitud de cuidado cancelada exitosamente. Se ha enviado un correo de confirmación de la cancelación.",
            },
            status=status.HTTP_200_OK,
        )


# class SolicitudCuidadoCreateView(generics.ListCreateAPIView):
#     queryset = SolicitudCuidado.objects.all()
#     permission_classes = [permissions.IsAuthenticated, IsClienteUser]
#     serializer_class = SolicitudCuidadoSerializer


from rest_framework.permissions import AllowAny


from rest_framework.permissions import AllowAny


class SolicitudCuidadoCreateView(generics.ListCreateAPIView):
    queryset = SolicitudCuidado.objects.all()
    serializer_class = SolicitudCuidadoSerializer
    permission_classes = [AllowAny]  # 🔹 Permitimos acceso al webhook sin autenticación

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            solicitud = serializer.save()

            # Datos de la solicitud
            solicitud_id = serializer.data["id"]
            email = (
                serializer.data.get("cliente", {})
                .get("user", {})
                .get("email", "No disponible")
            )
            mascota_nombre = serializer.data.get("mascota", {}).get(
                "nombre", "No disponible"
            )
            fecha_solicitud = serializer.data.get("fecha_solicitud", "No disponible")
            fecha_inicio = serializer.data.get("fecha_inicio", "No disponible")
            fecha_fin = serializer.data.get("fecha_fin", "No disponible")
            horas_cuidado = serializer.data.get("horas_cuidado", 0)
            is_cuidado_especial = serializer.data.get("is_cuidado_especial", False)
            descripcion = serializer.data.get("descripcion", "No disponible")
            costo = money_format(serializer.data.get("costo", 0))
            estado = serializer.data.get("estado", "Pendiente")

            # Verificar si el cuidador tiene información completa
            cuidador = serializer.data.get("cuidador", {})
            nombre_cuidador = f"{cuidador.get('primer_nombre', '')} {cuidador.get('segundo_nombre', '')} {cuidador.get('primer_apellido', '')} {cuidador.get('segundo_apellido', '')}".strip()

            try:
                send_care_email(
                    solicitud_id,
                    email,
                    mascota_nombre,
                    fecha_solicitud,
                    fecha_inicio,
                    fecha_fin,
                    horas_cuidado,
                    is_cuidado_especial,
                    descripcion,
                    costo,
                    estado,
                    nombre_cuidador,
                )
            except Exception as e:
                print(f"⚠️ Error al enviar correo: {e}")
                return Response(
                    {
                        "error": "Error al enviar correo",
                        "detail": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "message": "Solicitud de cuidado enviada correctamente. Debes esperar a la respuesta del cuidador."
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "error": serializer.errors,
                "message": "Error al enviar la solicitud de cuidado",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


## DONACIONES


# Donaciones de clientes
class DonacionesClienteView(generics.ListAPIView):
    serializer_class = DonacionSerializer
    permission_classes = [permissions.IsAuthenticated & IsClienteUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return Donacion.objects.filter(cliente__user=user)


# Donaciones de fundaciones


class DonacionesFundacionView(generics.ListAPIView):
    serializer_class = DonacionSerializer
    permission_classes = [permissions.IsAuthenticated & IsFundacionUser]

    def get_queryset(self):
        email = self.kwargs.get("email")
        user = get_object_or_404(User, email=email)
        return Donacion.objects.filter(fundacion__user=user)
