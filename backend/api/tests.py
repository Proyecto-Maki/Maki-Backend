from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from api.models import *
import json
from rest_framework.test import APIClient
from django.db.utils import IntegrityError


# class LocalidadModelTest(TestCase):
#     def setUp(self):
#         # Crear una instancia de Localidad para usar en los tests
#         self.localidad = Localidad.objects.create(nombre="Medellín")

#     def test_localidad_creation(self):
#         """Test para verificar que una localidad se crea correctamente"""
#         self.assertEqual(self.localidad.nombre, "Medellín")
#         self.assertIsInstance(self.localidad, Localidad)

#     def test_localidad_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         expected_str = f"{self.localidad.id} Medellín"
#         self.assertEqual(str(self.localidad), expected_str)

#     def test_localidad_nombre_max_length(self):
#         """Test para verificar que el campo nombre respeta el max_length"""
#         max_length = Localidad._meta.get_field("nombre").max_length
#         self.assertEqual(max_length, 255)

#     def test_crear_localidad_sin_nombre(self):
#         """Test para verificar que no se puede crear una localidad sin nombre"""
#         with self.assertRaises(IntegrityError):
#             Localidad.objects.create(nombre="")


# class DireccionModelTest(TestCase):
#     def setUp(self):
#         # Crear una instancia de Localidad para usar en los tests
#         self.localidad = Localidad.objects.create(nombre="Medellín")
#         # Crear una instancia de Direccion para usar en los tests
#         self.direccion = Direccion.objects.create(
#             direccion="Calle 123", codigo_postal="050001", localidad=self.localidad
#         )

#     def test_direccion_creation(self):
#         """Test para verificar que se puede crear una dirección correctamente"""
#         self.assertEqual(self.direccion.direccion, "Calle 123")
#         self.assertEqual(self.direccion.codigo_postal, "050001")
#         self.assertEqual(self.direccion.localidad, self.localidad)

#     def test_direccion_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         expected_str = "Calle 123 Medellín"
#         self.assertEqual(str(self.direccion), expected_str)

#     def test_direccion_codigo_postal_opcional(self):
#         """Test para verificar que el código postal es opcional"""
#         direccion_sin_cp = Direccion.objects.create(
#             direccion="Calle sin CP", localidad=self.localidad
#         )
#         self.assertIsNone(direccion_sin_cp.codigo_postal)
#         self.assertEqual(direccion_sin_cp.direccion, "Calle sin CP")


# class UserManagerTest(TestCase):
#     def setUp(self):
#         # Configuración inicial
#         self.user_data = {
#             "email": "user@example.com",
#             "password": "securepassword123",
#             "is_cliente": True,
#         }
#         self.superuser_data = {
#             "email": "admin@example.com",
#             "password": "adminpassword123",
#         }

#     def test_create_user(self):
#         """Test para verificar que se puede crear un usuario correctamente"""
#         user = User.objects.create_user(**self.user_data)
#         self.assertEqual(user.email, self.user_data["email"])
#         self.assertTrue(user.check_password(self.user_data["password"]))
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)

#     def test_create_user_without_email(self):
#         """Test para verificar que no se puede crear un usuario sin email"""
#         with self.assertRaises(ValueError) as e:
#             User.objects.create_user(email=None, password="password123")
#         self.assertEqual(str(e.exception), "El email es obligatorio")

#     def test_create_superuser(self):
#         """Test para verificar que se puede crear un superusuario correctamente"""
#         superuser = User.objects.create_superuser(**self.superuser_data)
#         self.assertEqual(superuser.email, self.superuser_data["email"])
#         self.assertTrue(superuser.check_password(self.superuser_data["password"]))
#         self.assertTrue(superuser.is_staff)
#         self.assertTrue(superuser.is_superuser)

#     def test_create_superuser_without_is_staff_or_is_superuser(self):
#         """Test para verificar que siempre se configuren is_staff e is_superuser en superusuarios"""
#         superuser = User.objects.create_superuser(**self.superuser_data)
#         self.assertTrue(superuser.is_staff)
#         self.assertTrue(superuser.is_superuser)


# class UserModelTest(TestCase):
#     def setUp(self):
#         # Crear una instancia de Localidad para usar en Direccion
#         self.localidad = Localidad.objects.create(nombre="Medellín")

#         # Crear una instancia de Direccion válida
#         self.direccion = Direccion.objects.create(
#             direccion="Calle 123",
#             codigo_postal="050001",
#             localidad=self.localidad,
#         )

#         # Datos base para usuarios
#         self.user_data = {
#             "email": "user@example.com",
#             "password": "securepassword123",
#             "is_cliente": True,
#             "direccion": self.direccion,
#             "telefono": "1234567890",
#             "saldo": 100.50,
#         }

#     def test_user_creation(self):
#         """Test para verificar que se puede crear un usuario correctamente"""
#         user = User.objects.create_user(**self.user_data)
#         self.assertEqual(user.email, self.user_data["email"])
#         self.assertTrue(user.check_password(self.user_data["password"]))
#         self.assertEqual(user.direccion, self.direccion)
#         self.assertEqual(user.telefono, "1234567890")
#         self.assertEqual(user.saldo, 100.50)
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)

#     def test_user_default_values(self):
#         """Test para verificar los valores predeterminados del usuario"""
#         user = User.objects.create_user(
#             email="default@example.com", password="password123"
#         )
#         self.assertTrue(user.is_active)
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)
#         self.assertFalse(user.is_cliente)
#         self.assertFalse(user.is_fundacion)
#         self.assertFalse(user.is_verified)
#         self.assertIsNone(user.direccion)
#         self.assertEqual(user.saldo, 0.00)

#     def test_user_str_method(self):
#         """Test para verificar que el método __str__ devuelve el email del usuario"""
#         user = User.objects.create_user(
#             email="strtest@example.com", password="password123"
#         )
#         self.assertEqual(str(user), "strtest@example.com")

#     def test_user_without_email(self):
#         """Test para verificar que no se puede crear un usuario sin email"""
#         with self.assertRaises(ValueError) as e:
#             User.objects.create_user(email=None, password="password123")
#         self.assertEqual(str(e.exception), "El email es obligatorio")

#     def test_superuser_creation(self):
#         """Test para verificar que se puede crear un superusuario correctamente"""
#         superuser = User.objects.create_superuser(
#             email="admin@example.com", password="adminpassword123"
#         )
#         self.assertTrue(superuser.is_staff)
#         self.assertTrue(superuser.is_superuser)


# class ClienteModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario base para asociar con el cliente
#         self.user = User.objects.create_user(
#             email="cliente@example.com", password="securepassword123"
#         )
#         # Crear un cliente
#         self.cliente = Cliente.objects.create(
#             user=self.user,
#             cedula=1234567890,
#             primer_nombre="Juan",
#             segundo_nombre="Carlos",
#             primer_apellido="Pérez",
#             segundo_apellido="Gómez",
#         )

#     def test_cliente_creation(self):
#         """Test para verificar que un cliente se crea correctamente"""
#         self.assertEqual(self.cliente.user, self.user)
#         self.assertEqual(self.cliente.cedula, 1234567890)
#         self.assertEqual(self.cliente.primer_nombre, "Juan")
#         self.assertEqual(self.cliente.segundo_nombre, "Carlos")
#         self.assertEqual(self.cliente.primer_apellido, "Pérez")
#         self.assertEqual(self.cliente.segundo_apellido, "Gómez")

#     def test_cliente_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         expected_str = "Juan Pérez"
#         self.assertEqual(str(self.cliente), expected_str)

#     def test_cliente_without_optional_fields(self):
#         """Test para verificar que un cliente se puede crear con solo los campos obligatorios"""
#         user = User.objects.create_user(
#             email="simplecliente@example.com", password="password123"
#         )
#         cliente = Cliente.objects.create(user=user)
#         self.assertIsNone(cliente.cedula)
#         self.assertIsNone(cliente.primer_nombre)
#         self.assertIsNone(cliente.segundo_nombre)
#         self.assertIsNone(cliente.primer_apellido)
#         self.assertIsNone(cliente.segundo_apellido)


# class FundacionModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario base para asociar con la fundación
#         self.user = User.objects.create_user(
#             email="fundacion@example.com", password="securepassword123"
#         )
#         # Crear una fundación
#         self.fundacion = Fundacion.objects.create(
#             user=self.user,
#             nombre="Fundación Amigos",
#             nit="123456789-0",
#             descripcion="Una fundación dedicada al bienestar animal.",
#             premium=True,
#         )

#     def test_fundacion_creation(self):
#         """Test para verificar que una fundación se crea correctamente"""
#         self.assertEqual(self.fundacion.user, self.user)
#         self.assertEqual(self.fundacion.nombre, "Fundación Amigos")
#         self.assertEqual(self.fundacion.nit, "123456789-0")
#         self.assertEqual(
#             self.fundacion.descripcion, "Una fundación dedicada al bienestar animal."
#         )
#         self.assertTrue(self.fundacion.premium)

#     def test_fundacion_str_method(self):
#         """Test para verificar que el método __str__ devuelve el nombre de la fundación"""
#         self.assertEqual(str(self.fundacion), "Fundación Amigos")

#     def test_fundacion_without_optional_fields(self):
#         """Test para verificar que una fundación se puede crear con solo los campos obligatorios"""
#         user = User.objects.create_user(
#             email="simplefundacion@example.com", password="password123"
#         )
#         fundacion = Fundacion.objects.create(user=user)
#         self.assertIsNone(fundacion.nombre)
#         self.assertIsNone(fundacion.nit)
#         self.assertIsNone(fundacion.descripcion)
#         self.assertFalse(fundacion.premium)


# class MascotaModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para asociar con las mascotas
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Datos base para mascotas
#         self.mascota_data = {
#             "user": self.user,
#             "nombre": "Rex",
#             "sexo": "M",
#             "tipo": "Perro",
#             "raza": "Labrador",
#             "edad": 3,
#             "estado_salud": "Saludable",
#             "tamano": "G",
#             "peso": 30.5,
#         }

#     def test_mascota_creation(self):
#         """Test para verificar que se puede crear una mascota correctamente"""
#         mascota = Mascota.objects.create(**self.mascota_data)
#         self.assertEqual(mascota.nombre, "Rex")
#         self.assertEqual(mascota.sexo, "M")
#         self.assertEqual(mascota.tipo, "Perro")
#         self.assertEqual(mascota.raza, "Labrador")
#         self.assertEqual(mascota.edad, 3)
#         self.assertEqual(mascota.estado_salud, "Saludable")
#         self.assertEqual(mascota.tamano, "G")
#         self.assertEqual(mascota.peso, 30.5)

#     def test_mascota_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         mascota = Mascota.objects.create(**self.mascota_data)
#         expected_str = f"{mascota.id} Rex"
#         self.assertEqual(str(mascota), expected_str)

#     def test_mascota_invalid_sexo(self):
#         """Test para verificar que no se puede asignar un sexo no válido"""
#         invalid_data = self.mascota_data.copy()
#         invalid_data["sexo"] = "X"
#         mascota = Mascota(**invalid_data)
#         with self.assertRaises(ValidationError):
#             mascota.full_clean()

#     def test_mascota_invalid_estado_salud(self):
#         """Test para verificar que no se puede asignar un estado de salud no válido"""
#         invalid_data = self.mascota_data.copy()
#         invalid_data["estado_salud"] = "Desconocido"
#         mascota = Mascota(**invalid_data)
#         with self.assertRaises(ValidationError):
#             mascota.full_clean()

#     def test_mascota_imagen_opcional(self):
#         """Test para verificar que la imagen es opcional"""
#         mascota = Mascota.objects.create(**self.mascota_data)
#         self.assertIsNone(mascota.imagen)

#     def test_mascota_invalid_tamano(self):
#         """Test para verificar que no se puede asignar un tamaño no válido"""
#         invalid_data = self.mascota_data.copy()
#         invalid_data["tamano"] = "X"
#         mascota = Mascota(**invalid_data)
#         with self.assertRaises(ValidationError):
#             mascota.full_clean()


# class PadecimientoModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para asociar con la mascota
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Crear una mascota para asociar con los padecimientos
#         self.mascota = Mascota.objects.create(
#             user=self.user,
#             nombre="Rex",
#             sexo="M",
#             tipo="Perro",
#             raza="Labrador",
#             edad=3,
#             estado_salud="Saludable",
#             tamano="G",
#             peso=30.5,
#         )
#         # Datos base para padecimientos
#         self.padecimiento_data = {
#             "mascota": self.mascota,
#             "padecimiento": "Parvovirus",
#         }

#     def test_padecimiento_creation(self):
#         """Test para verificar que se puede crear un padecimiento correctamente"""
#         padecimiento = Padecimiento.objects.create(**self.padecimiento_data)
#         self.assertEqual(padecimiento.mascota, self.mascota)
#         self.assertEqual(padecimiento.padecimiento, "Parvovirus")

#     def test_padecimiento_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         padecimiento = Padecimiento.objects.create(**self.padecimiento_data)
#         expected_str = f"{self.mascota.nombre} - Parvovirus"
#         self.assertEqual(str(padecimiento), expected_str)

#     def test_padecimiento_sin_padecimiento(self):
#         """Test para verificar que no se puede crear un padecimiento sin descripción"""
#         invalid_data = self.padecimiento_data.copy()
#         invalid_data["padecimiento"] = ""
#         padecimiento = Padecimiento(**invalid_data)
#         with self.assertRaises(ValidationError):
#             padecimiento.full_clean()

#     def test_padecimiento_sin_mascota(self):
#         """Test para verificar que no se puede crear un padecimiento sin mascota"""
#         invalid_data = self.padecimiento_data.copy()
#         invalid_data["mascota"] = None
#         with self.assertRaises(Exception):
#             Padecimiento.objects.create(**invalid_data)


# class ProductoModelTest(TestCase):
#     def setUp(self):
#         # Datos base para los productos
#         self.producto_data = {
#             "nombre": "Croquetas de pollo",
#             "descripcion": "Deliciosas croquetas de pollo para mascotas.",
#             "precio": 49.99,
#             "stock": 10,
#             "categoria": "Alimentos",
#             "ingredientes": "Pollo, cereales, vitaminas",
#         }

#     def test_producto_creation(self):
#         """Test para verificar que se puede crear un producto correctamente"""
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertEqual(producto.nombre, "Croquetas de pollo")
#         self.assertEqual(
#             producto.descripcion, "Deliciosas croquetas de pollo para mascotas."
#         )
#         self.assertEqual(producto.precio, 49.99)
#         self.assertEqual(producto.stock, 10)
#         self.assertEqual(producto.categoria, "Alimentos")
#         self.assertEqual(producto.ingredientes, "Pollo, cereales, vitaminas")

#     def test_producto_slug_autogeneration(self):
#         """Test para verificar que el slug se genera automáticamente si no se proporciona"""
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertEqual(producto.slug, "croquetas-de-pollo")

#     def test_producto_slug_custom(self):
#         """Test para verificar que el slug no se sobrescribe si se proporciona uno personalizado"""
#         self.producto_data["slug"] = "custom-slug"
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertEqual(producto.slug, "custom-slug")

#     def test_producto_str_method(self):
#         """Test para verificar que el método __str__ devuelve el nombre del producto"""
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertEqual(str(producto), "Croquetas de pollo")

#     def test_producto_imagen_opcional(self):
#         """Test para verificar que la imagen es un campo opcional"""
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertIsNone(producto.imagen)

#     def test_producto_precio_por_defecto(self):
#         """Test para verificar que el precio por defecto es 0.00"""
#         self.producto_data.pop("precio")  # Remover el precio de los datos iniciales
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertEqual(producto.precio, 0.00)

#     def test_producto_stock_por_defecto(self):
#         """Test para verificar que el stock por defecto es 0"""
#         self.producto_data.pop("stock")  # Remover el stock de los datos iniciales
#         producto = Producto.objects.create(**self.producto_data)
#         self.assertEqual(producto.stock, 0)


# class CarritoModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para asociar con los carritos
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Datos base para los carritos
#         self.carrito_data = {
#             "codigo": "CART12345",
#             "user": self.user,
#             "pagado": False,
#         }

#     def test_carrito_creation(self):
#         """Test para verificar que se puede crear un carrito correctamente"""
#         carrito = Carrito.objects.create(**self.carrito_data)
#         self.assertEqual(carrito.codigo, "CART12345")
#         self.assertEqual(carrito.user, self.user)
#         self.assertFalse(carrito.pagado)

#     def test_carrito_str_method(self):
#         """Test para verificar que el método __str__ devuelve el código del carrito"""
#         carrito = Carrito.objects.create(**self.carrito_data)
#         self.assertEqual(str(carrito), "CART12345")

#     def test_carrito_pagado_default(self):
#         """Test para verificar que el campo 'pagado' por defecto es False"""
#         self.carrito_data.pop(
#             "pagado"
#         )  # Remover el campo 'pagado' de los datos iniciales
#         carrito = Carrito.objects.create(**self.carrito_data)
#         self.assertFalse(carrito.pagado)

#     def test_carrito_sin_usuario(self):
#         """Test para verificar que se puede crear un carrito sin usuario asociado"""
#         self.carrito_data["user"] = None
#         carrito = Carrito.objects.create(**self.carrito_data)
#         self.assertIsNone(carrito.user)

#     def test_carrito_fecha_creado(self):
#         """Test para verificar que 'creado' se asigna automáticamente al crear el carrito"""
#         carrito = Carrito.objects.create(**self.carrito_data)
#         self.assertIsNotNone(carrito.creado)

#     def test_carrito_fecha_modificado(self):
#         """Test para verificar que 'modificado' se actualiza automáticamente"""
#         carrito = Carrito.objects.create(**self.carrito_data)
#         fecha_modificado_original = carrito.modificado
#         carrito.pagado = True
#         carrito.save()
#         self.assertNotEqual(carrito.modificado, fecha_modificado_original)


# class ItemCarritoModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para asociar con el carrito
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Crear un carrito
#         self.carrito = Carrito.objects.create(codigo="CART12345", user=self.user)
#         # Crear un producto
#         self.producto = Producto.objects.create(
#             nombre="Croquetas de pollo",
#             descripcion="Deliciosas croquetas para mascotas.",
#             precio=49.99,
#             stock=100,
#             categoria="Alimentos",
#         )
#         # Datos base para los items del carrito
#         self.item_carrito_data = {
#             "carrito": self.carrito,
#             "producto": self.producto,
#             "cantidad": 3,
#         }

#     def test_item_carrito_creation(self):
#         """Test para verificar que se puede crear un item en el carrito correctamente"""
#         item = ItemCarrito.objects.create(**self.item_carrito_data)
#         self.assertEqual(item.carrito, self.carrito)
#         self.assertEqual(item.producto, self.producto)
#         self.assertEqual(item.cantidad, 3)

#     def test_item_carrito_default_cantidad(self):
#         """Test para verificar que el valor predeterminado de cantidad es 1"""
#         self.item_carrito_data.pop("cantidad")  # Eliminar el campo 'cantidad'
#         item = ItemCarrito.objects.create(**self.item_carrito_data)
#         self.assertEqual(item.cantidad, 1)

#     def test_item_carrito_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         item = ItemCarrito.objects.create(**self.item_carrito_data)
#         expected_str = "3 x Croquetas de pollo en carrito CART12345"
#         self.assertEqual(str(item), expected_str)

#     def test_item_carrito_negativa_cantidad(self):
#         """Test para verificar que no se pueda crear un item con cantidad negativa"""
#         self.item_carrito_data["cantidad"] = -5
#         item = ItemCarrito(**self.item_carrito_data)
#         with self.assertRaises(ValidationError):
#             item.full_clean()  # Llama a las validaciones personalizadas

#     def test_item_carrito_sin_producto(self):
#         """Test para verificar que no se pueda crear un item sin un producto"""
#         self.item_carrito_data["producto"] = None
#         with self.assertRaises(Exception):
#             ItemCarrito.objects.create(**self.item_carrito_data)

#     def test_item_carrito_sin_carrito(self):
#         """Test para verificar que no se pueda crear un item sin un carrito"""
#         self.item_carrito_data["carrito"] = None
#         with self.assertRaises(Exception):
#             ItemCarrito.objects.create(**self.item_carrito_data)


# class PedidoModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para asociar con los pedidos
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Crear un descuento para pruebas
#         self.descuento = Descuento.objects.create(
#             descripcion="Descuento de prueba", porcentaje=10.00
#         )
#         # Datos base para los pedidos
#         self.pedido_data = {
#             "user": self.user,
#             "estado": "Preparación",
#             "descuento": self.descuento,
#             "total": 100.00,
#         }

#     def test_pedido_creation(self):
#         """Test para verificar que se puede crear un pedido correctamente"""
#         pedido = Pedido.objects.create(**self.pedido_data)
#         self.assertEqual(pedido.user, self.user)
#         self.assertEqual(pedido.estado, "Preparación")
#         self.assertEqual(pedido.descuento, self.descuento)
#         self.assertEqual(pedido.total, 100.00)

#     def test_pedido_estado_default(self):
#         """Test para verificar que el estado por defecto es 'Preparación'"""
#         self.pedido_data.pop("estado")  # Eliminar el estado de los datos iniciales
#         pedido = Pedido.objects.create(**self.pedido_data)
#         self.assertEqual(pedido.estado, "Preparación")

#     def test_pedido_sin_descuento(self):
#         """Test para verificar que un pedido puede crearse sin descuento"""
#         self.pedido_data["descuento"] = None
#         pedido = Pedido.objects.create(**self.pedido_data)
#         self.assertIsNone(pedido.descuento)

#     def test_pedido_fecha_creado(self):
#         """Test para verificar que 'fecha' se asigna automáticamente al crear el pedido"""
#         pedido = Pedido.objects.create(**self.pedido_data)
#         self.assertIsNotNone(pedido.fecha)

#     def test_pedido_str_method(self):
#         """Test para verificar que el método __str__ devuelve el ID del pedido como cadena"""
#         pedido = Pedido.objects.create(**self.pedido_data)
#         self.assertEqual(str(pedido), str(pedido.id))

#     def test_pedido_estado_invalido(self):
#         """Test para verificar que no se puede asignar un estado no válido"""
#         self.pedido_data["estado"] = "Invalido"
#         pedido = Pedido(**self.pedido_data)
#         with self.assertRaises(ValidationError):
#             pedido.full_clean()  # Valida los datos antes de guardar


# class DetallePedidoModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para asociar con el pedido
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Crear un descuento para el pedido
#         self.descuento = Descuento.objects.create(
#             descripcion="Descuento de prueba", porcentaje=10.00
#         )
#         # Crear un pedido
#         self.pedido = Pedido.objects.create(
#             user=self.user,
#             estado="Preparación",
#             descuento=self.descuento,
#             total=100.00,
#         )
#         # Crear un producto
#         self.producto = Producto.objects.create(
#             nombre="Croquetas de pollo",
#             descripcion="Deliciosas croquetas para mascotas.",
#             precio=49.99,
#             stock=100,
#             categoria="Alimentos",
#         )
#         # Datos base para los detalles del pedido
#         self.detalle_pedido_data = {
#             "pedido": self.pedido,
#             "producto": self.producto,
#             "cantidad": 3,
#         }

#     def test_detalle_pedido_creation(self):
#         """Test para verificar que se puede crear un detalle de pedido correctamente"""
#         detalle = DetallePedido.objects.create(**self.detalle_pedido_data)
#         self.assertEqual(detalle.pedido, self.pedido)
#         self.assertEqual(detalle.producto, self.producto)
#         self.assertEqual(detalle.cantidad, 3)

#     def test_detalle_pedido_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         detalle = DetallePedido.objects.create(**self.detalle_pedido_data)
#         expected_str = f"{self.producto.nombre} x 3"
#         self.assertEqual(str(detalle), expected_str)

#     def test_detalle_pedido_cantidad_invalida(self):
#         """Test para verificar que no se pueda asignar una cantidad negativa"""
#         self.detalle_pedido_data["cantidad"] = -5
#         detalle = DetallePedido(**self.detalle_pedido_data)
#         with self.assertRaises(ValidationError):
#             detalle.full_clean()  # Llama a las validaciones personalizadas

#     def test_detalle_pedido_sin_producto(self):
#         """Test para verificar que no se pueda crear un detalle de pedido sin producto"""
#         self.detalle_pedido_data["producto"] = None
#         with self.assertRaises(Exception):
#             DetallePedido.objects.create(**self.detalle_pedido_data)

#     def test_detalle_pedido_sin_pedido(self):
#         """Test para verificar que no se pueda crear un detalle de pedido sin pedido"""
#         self.detalle_pedido_data["pedido"] = None
#         with self.assertRaises(Exception):
#             DetallePedido.objects.create(**self.detalle_pedido_data)


# class CuidadorModelTest(TestCase):
#     def setUp(self):
#         # Datos base para los cuidadores
#         self.cuidador_data = {
#             "cedula": 1234567890,
#             "primer_nombre": "Juan",
#             "segundo_nombre": "Carlos",
#             "primer_apellido": "Pérez",
#             "segundo_apellido": "Gómez",
#             "telefono": "1234567890",
#             "direccion": "Calle 123",
#             "email": "juan.perez@example.com",
#             "ocupacion": "Veterinario",
#             "experiencia": "10 años trabajando con animales.",
#             "descripcion_servicio": "Cuidado especializado para mascotas.",
#         }

#     def test_cuidador_creation(self):
#         """Test para verificar que se puede crear un cuidador correctamente"""
#         cuidador = Cuidador.objects.create(**self.cuidador_data)
#         self.assertEqual(cuidador.cedula, 1234567890)
#         self.assertEqual(cuidador.primer_nombre, "Juan")
#         self.assertEqual(cuidador.segundo_nombre, "Carlos")
#         self.assertEqual(cuidador.primer_apellido, "Pérez")
#         self.assertEqual(cuidador.segundo_apellido, "Gómez")
#         self.assertEqual(cuidador.telefono, "1234567890")
#         self.assertEqual(cuidador.direccion, "Calle 123")
#         self.assertEqual(cuidador.email, "juan.perez@example.com")
#         self.assertEqual(cuidador.ocupacion, "Veterinario")
#         self.assertEqual(cuidador.experiencia, "10 años trabajando con animales.")
#         self.assertEqual(
#             cuidador.descripcion_servicio, "Cuidado especializado para mascotas."
#         )

#     def test_cuidador_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         cuidador = Cuidador.objects.create(**self.cuidador_data)
#         expected_str = "Juan Pérez"
#         self.assertEqual(str(cuidador), expected_str)

#     def test_cuidador_cedula_unica(self):
#         """Test para verificar que la cédula debe ser única"""
#         Cuidador.objects.create(**self.cuidador_data)
#         with self.assertRaises(Exception):
#             Cuidador.objects.create(**self.cuidador_data)

#     def test_cuidador_email_unico(self):
#         """Test para verificar que el email debe ser único"""
#         Cuidador.objects.create(**self.cuidador_data)
#         self.cuidador_data["cedula"] = (
#             9876543210  # Cambiar la cédula para evitar conflicto
#         )
#         with self.assertRaises(Exception):
#             Cuidador.objects.create(**self.cuidador_data)

#     def test_cuidador_campos_obligatorios(self):
#         """Test para verificar que los campos obligatorios no pueden estar vacíos"""
#         campos_obligatorios = [
#             "cedula",
#             "primer_nombre",
#             "primer_apellido",
#             "telefono",
#             "direccion",
#             "email",
#             "ocupacion",
#             "experiencia",
#             "descripcion_servicio",
#         ]
#         for campo in campos_obligatorios:
#             datos_invalidos = self.cuidador_data.copy()
#             datos_invalidos[campo] = None
#             with self.assertRaises(Exception):
#                 Cuidador.objects.create(**datos_invalidos)


# class CuidadorModelTest(TestCase):
#     def setUp(self):
#         # Datos base para los cuidadores
#         self.cuidador_data = {
#             "cedula": 1234567890,
#             "primer_nombre": "Juan",
#             "segundo_nombre": "Carlos",
#             "primer_apellido": "Pérez",
#             "segundo_apellido": "Gómez",
#             "telefono": "1234567890",
#             "direccion": "Calle 123",
#             "email": "juan.perez@example.com",
#             "ocupacion": "Veterinario",
#             "experiencia": "10 años trabajando con animales.",
#             "descripcion_servicio": "Cuidado especializado para mascotas.",
#         }

#     def test_cuidador_creation(self):
#         """Test para verificar que se puede crear un cuidador correctamente"""
#         cuidador = Cuidador.objects.create(**self.cuidador_data)
#         self.assertEqual(cuidador.cedula, 1234567890)
#         self.assertEqual(cuidador.primer_nombre, "Juan")
#         self.assertEqual(cuidador.segundo_nombre, "Carlos")
#         self.assertEqual(cuidador.primer_apellido, "Pérez")
#         self.assertEqual(cuidador.segundo_apellido, "Gómez")
#         self.assertEqual(cuidador.telefono, "1234567890")
#         self.assertEqual(cuidador.direccion, "Calle 123")
#         self.assertEqual(cuidador.email, "juan.perez@example.com")
#         self.assertEqual(cuidador.ocupacion, "Veterinario")
#         self.assertEqual(cuidador.experiencia, "10 años trabajando con animales.")
#         self.assertEqual(
#             cuidador.descripcion_servicio, "Cuidado especializado para mascotas."
#         )

#     def test_cuidador_str_method(self):
#         """Test para verificar que el método __str__ devuelve el formato correcto"""
#         cuidador = Cuidador.objects.create(**self.cuidador_data)
#         expected_str = "Juan Pérez"
#         self.assertEqual(str(cuidador), expected_str)

#     def test_cuidador_cedula_unica(self):
#         """Test para verificar que la cédula debe ser única"""
#         Cuidador.objects.create(**self.cuidador_data)
#         with self.assertRaises(Exception):
#             Cuidador.objects.create(**self.cuidador_data)

#     def test_cuidador_email_unico(self):
#         """Test para verificar que el email debe ser único"""
#         Cuidador.objects.create(**self.cuidador_data)
#         self.cuidador_data["cedula"] = (
#             9876543210  # Cambiar la cédula para evitar conflicto
#         )
#         with self.assertRaises(Exception):
#             Cuidador.objects.create(**self.cuidador_data)

#     def test_cuidador_campos_obligatorios(self):
#         """Test para verificar que los campos obligatorios no pueden estar vacíos"""
#         campos_obligatorios = [
#             "cedula",
#             "primer_nombre",
#             "primer_apellido",
#             "telefono",
#             "direccion",
#             "email",
#             "ocupacion",
#             "experiencia",
#             "descripcion_servicio",
#         ]
#         for campo in campos_obligatorios:
#             datos_invalidos = self.cuidador_data.copy()
#             datos_invalidos[campo] = None
#             with self.assertRaises(Exception):
#                 Cuidador.objects.create(**datos_invalidos)

#     def test_cuidador_segundo_nombre_opcional(self):
#         """Test para verificar que el segundo nombre es opcional"""
#         self.cuidador_data["segundo_nombre"] = None
#         cuidador = Cuidador.objects.create(**self.cuidador_data)
#         self.assertIsNone(cuidador.segundo_nombre)

#     def test_cuidador_segundo_apellido_opcional(self):
#         """Test para verificar que el segundo apellido es opcional"""
#         self.cuidador_data["segundo_apellido"] = None
#         cuidador = Cuidador.objects.create(**self.cuidador_data)
#         self.assertIsNone(cuidador.segundo_apellido)


# class SolicitudCuidadoModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para el cliente
#         self.user_cliente = User.objects.create_user(
#             email="cliente@example.com", password="securepassword123"
#         )
#         # Crear un usuario para el cuidador
#         self.user_cuidador = User.objects.create_user(
#             email="cuidador@example.com", password="securepassword123"
#         )
#         # Crear un cliente
#         self.cliente = Cliente.objects.create(
#             user=self.user_cliente,
#             cedula=1234567890,
#             primer_nombre="Juan",
#             primer_apellido="Pérez",
#         )
#         # Crear un cuidador
#         self.cuidador = Cuidador.objects.create(
#             cedula=987654321,
#             primer_nombre="Carlos",
#             primer_apellido="Gómez",
#             telefono="1234567890",
#             direccion="Calle 123",
#             email="cuidador@example.com",
#             ocupacion="Veterinario",
#             experiencia="5 años cuidando animales.",
#             descripcion_servicio="Cuidado de mascotas 24/7.",
#         )
#         # Crear una mascota
#         self.mascota = Mascota.objects.create(
#             user=self.user_cliente,
#             nombre="Rex",
#             sexo="M",
#             tipo="Perro",
#             raza="Labrador",
#             edad=3,
#             estado_salud="Saludable",
#             tamano="G",
#             peso=30.5,
#         )
#         # Datos base para las solicitudes de cuidado
#         self.solicitud_data = {
#             "cuidador": self.cuidador,
#             "cliente": self.cliente,
#             "mascota": self.mascota,
#             "fecha_inicio": "2025-01-15",
#             "fecha_fin": "2025-01-20",
#             "descripcion": "Cuidado intensivo durante las vacaciones.",
#             "estado": "Pendiente",
#         }

#     def test_solicitud_cuidado_creation(self):
#         """Test para verificar que se puede crear una solicitud de cuidado correctamente"""
#         solicitud = SolicitudCuidado.objects.create(**self.solicitud_data)
#         self.assertEqual(solicitud.cuidador, self.cuidador)
#         self.assertEqual(solicitud.cliente, self.cliente)
#         self.assertEqual(solicitud.mascota, self.mascota)
#         self.assertEqual(solicitud.fecha_inicio, "2025-01-15")
#         self.assertEqual(solicitud.fecha_fin, "2025-01-20")
#         self.assertEqual(
#             solicitud.descripcion, "Cuidado intensivo durante las vacaciones."
#         )
#         self.assertEqual(solicitud.estado, "Pendiente")

#     def test_solicitud_estado_invalido(self):
#         """Test para verificar que no se puede asignar un estado no válido"""
#         self.solicitud_data["estado"] = "No válido"
#         with self.assertRaises(ValidationError):
#             solicitud = SolicitudCuidado(**self.solicitud_data)
#             solicitud.full_clean()  # Ejecuta validaciones manualmente antes de guardar

#     def test_solicitud_fecha_inicio_obligatoria(self):
#         """Test para verificar que la fecha de inicio es obligatoria"""
#         self.solicitud_data["fecha_inicio"] = None
#         with self.assertRaises(Exception):
#             SolicitudCuidado.objects.create(**self.solicitud_data)

#     def test_solicitud_fecha_fin_obligatoria(self):
#         """Test para verificar que la fecha de fin es obligatoria"""
#         self.solicitud_data["fecha_fin"] = None
#         with self.assertRaises(Exception):
#             SolicitudCuidado.objects.create(**self.solicitud_data)

#     def test_solicitud_descripcion_obligatoria(self):
#         """Test para verificar que la descripción es obligatoria"""
#         self.solicitud_data["descripcion"] = ""
#         with self.assertRaises(ValidationError):
#             solicitud = SolicitudCuidado(**self.solicitud_data)
#             solicitud.full_clean()  # Ejecuta validaciones manualmente antes de guardar

#     def test_solicitud_cuidador_cliente_obligatorios(self):
#         """Test para verificar que tanto el cuidador como el cliente son obligatorios"""
#         self.solicitud_data["cuidador"] = None
#         with self.assertRaises(Exception):
#             SolicitudCuidado.objects.create(**self.solicitud_data)

#         self.solicitud_data["cuidador"] = self.cuidador
#         self.solicitud_data["cliente"] = None
#         with self.assertRaises(Exception):
#             SolicitudCuidado.objects.create(**self.solicitud_data)

#     def test_solicitud_mascota_obligatoria(self):
#         """Test para verificar que la mascota es obligatoria"""
#         self.solicitud_data["mascota"] = None
#         with self.assertRaises(Exception):
#             SolicitudCuidado.objects.create(**self.solicitud_data)


# class ResenaModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario
#         self.user = User.objects.create_user(
#             email="user@example.com", password="securepassword123"
#         )
#         # Crear un producto
#         self.producto = Producto.objects.create(
#             nombre="Producto de prueba",
#             descripcion="Descripción del producto",
#             precio=19.99,
#             stock=10,
#             categoria="General",
#         )
#         # Datos base para las reseñas
#         self.resena_data = {
#             "user": self.user,
#             "producto": self.producto,
#             "titulo": "Buena calidad",
#             "calificacion": 4,
#             "comentario": "Me gustó mucho este producto.",
#         }

#     def test_resena_creation(self):
#         """Test para verificar que se puede crear una reseña correctamente"""
#         resena = Resena.objects.create(**self.resena_data)
#         self.assertEqual(resena.user, self.user)
#         self.assertEqual(resena.producto, self.producto)
#         self.assertEqual(resena.titulo, "Buena calidad")
#         self.assertEqual(resena.calificacion, 4)
#         self.assertEqual(resena.comentario, "Me gustó mucho este producto.")

#     def test_resena_calificacion_fuera_de_rango(self):
#         """Test para verificar que no se puede asignar una calificación fuera del rango permitido"""
#         self.resena_data["calificacion"] = 6  # Valor fuera del rango permitido
#         resena = Resena(**self.resena_data)
#         with self.assertRaises(ValidationError):
#             resena.full_clean()  # Activa las validaciones de rango

#         self.resena_data["calificacion"] = 0  # Otro valor fuera del rango
#         resena = Resena(**self.resena_data)
#         with self.assertRaises(ValidationError):
#             resena.full_clean()

#     def test_resena_titulo_por_defecto(self):
#         """Test para verificar que el título por defecto sea 'Sin titulo' si no se especifica"""
#         self.resena_data.pop("titulo")
#         resena = Resena.objects.create(**self.resena_data)
#         self.assertEqual(resena.titulo, "Sin titulo")

#     def test_resena_comentario_opcional(self):
#         """Test para verificar que el comentario sea opcional"""
#         self.resena_data["comentario"] = None
#         resena = Resena.objects.create(**self.resena_data)
#         self.assertIsNone(resena.comentario)

#     def test_resena_usuario_obligatorio(self):
#         """Test para verificar que el usuario es obligatorio"""
#         self.resena_data["user"] = None
#         resena = Resena(**self.resena_data)
#         with self.assertRaises(ValidationError):
#             resena.full_clean()

#     def test_resena_producto_obligatorio(self):
#         """Test para verificar que el producto es obligatorio"""
#         self.resena_data["producto"] = None
#         resena = Resena(**self.resena_data)
#         with self.assertRaises(ValidationError):
#             resena.full_clean()

#     def test_resena_fecha_auto_asignada(self):
#         """Test para verificar que la fecha se asigna automáticamente al crear la reseña"""
#         resena = Resena.objects.create(**self.resena_data)
#         self.assertIsNotNone(resena.fecha)


# class TarjetaModelTest(TestCase):
#     def setUp(self):
#         # Datos base para las tarjetas
#         self.tarjeta_data = {
#             "tipo": "Débito",
#             "monto": 100.00,
#         }

#     def test_tarjeta_creation(self):
#         """Test para verificar que se puede crear una tarjeta correctamente"""
#         tarjeta = Tarjeta.objects.create(**self.tarjeta_data)
#         self.assertEqual(tarjeta.tipo, "Débito")
#         self.assertEqual(tarjeta.monto, 100.00)

#     def test_tarjeta_tipo_obligatorio(self):
#         """Test para verificar que el campo 'tipo' es obligatorio"""
#         self.tarjeta_data["tipo"] = None
#         tarjeta = Tarjeta(**self.tarjeta_data)
#         with self.assertRaises(ValidationError):
#             tarjeta.full_clean()  # Activa las validaciones

#     def test_tarjeta_monto_defecto(self):
#         """Test para verificar que el campo 'monto' tiene un valor por defecto de 0.00"""
#         self.tarjeta_data.pop("monto")  # Elimina el campo 'monto'
#         tarjeta = Tarjeta.objects.create(**self.tarjeta_data)
#         self.assertEqual(tarjeta.monto, 0.00)

#     def test_tarjeta_monto_negativo(self):
#         """Test para verificar que no se permite un monto negativo"""
#         self.tarjeta_data["monto"] = -50.00  # Monto negativo
#         tarjeta = Tarjeta(**self.tarjeta_data)
#         with self.assertRaises(ValidationError):
#             tarjeta.full_clean()

#     def test_tarjeta_tipo_unico(self):
#         """Test para verificar que el campo 'tipo' es único (primary key)"""
#         Tarjeta.objects.create(**self.tarjeta_data)
#         with self.assertRaises(Exception):  # IntegrityError o similar
#             Tarjeta.objects.create(**self.tarjeta_data)

#     def test_tarjeta_str_method(self):
#         """Test para verificar que el método __str__ retorna el tipo de la tarjeta"""
#         tarjeta = Tarjeta.objects.create(**self.tarjeta_data)
#         self.assertEqual(str(tarjeta), "Débito")


# class DonacionModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para el cliente
#         self.user_cliente = User.objects.create_user(
#             email="cliente@example.com", password="securepassword123"
#         )
#         # Crear un cliente
#         self.cliente = Cliente.objects.create(
#             user=self.user_cliente,
#             cedula=1234567890,
#             primer_nombre="Juan",
#             primer_apellido="Pérez",
#         )

#         # Crear un usuario para la fundación
#         self.user_fundacion = User.objects.create_user(
#             email="fundacion@example.com", password="securepassword123"
#         )
#         # Crear una fundación
#         self.fundacion = Fundacion.objects.create(
#             user=self.user_fundacion,
#             nombre="Fundación Ejemplo",
#             nit="123456789",
#             descripcion="Fundación para animales.",
#         )

#         # Crear una tarjeta
#         self.tarjeta = Tarjeta.objects.create(
#             tipo="Débito",
#             monto=100.00,
#         )

#         # Datos base para donaciones
#         self.donacion_data = {
#             "cliente": self.cliente,
#             "fundacion": self.fundacion,
#             "tarjeta": self.tarjeta,
#         }

#     def test_donacion_creation(self):
#         """Test para verificar que se puede crear una donación correctamente"""
#         donacion = Donacion.objects.create(**self.donacion_data)
#         self.assertEqual(donacion.cliente, self.cliente)
#         self.assertEqual(donacion.fundacion, self.fundacion)
#         self.assertEqual(donacion.tarjeta, self.tarjeta)
#         self.assertIsNotNone(donacion.fecha)  # Fecha autoasignada

#     def test_donacion_cliente_obligatorio(self):
#         """Test para verificar que el cliente es obligatorio"""
#         self.donacion_data["cliente"] = None
#         with self.assertRaises(Exception):
#             Donacion.objects.create(**self.donacion_data)

#     def test_donacion_fundacion_obligatoria(self):
#         """Test para verificar que la fundación es obligatoria"""
#         self.donacion_data["fundacion"] = None
#         with self.assertRaises(Exception):
#             Donacion.objects.create(**self.donacion_data)

#     def test_donacion_tarjeta_obligatoria(self):
#         """Test para verificar que la tarjeta es obligatoria"""
#         self.donacion_data["tarjeta"] = None
#         with self.assertRaises(Exception):
#             Donacion.objects.create(**self.donacion_data)

#     def test_donacion_fecha_auto_asignada(self):
#         """Test para verificar que la fecha se asigna automáticamente al crear la donación"""
#         donacion = Donacion.objects.create(**self.donacion_data)
#         self.assertIsNotNone(donacion.fecha)

#     def test_donacion_str_method(self):
#         """Test para verificar que el método __str__ retorna el formato esperado"""
#         donacion = Donacion.objects.create(**self.donacion_data)
#         self.assertEqual(
#             str(donacion),
#             f"Donacion de {self.cliente.primer_nombre} {self.cliente.primer_apellido} para {self.fundacion.nombre}",
#         )


# class PublicacionAdopcionModelTest(TestCase):
#     def setUp(self):
#         self.localidad = Localidad.objects.create(nombre="Localidad Ejemplo")
#         self.direccion = Direccion.objects.create(
#             direccion="Calle 123",
#             codigo_postal="12345",
#             localidad=self.localidad,  # Usar la localidad creada
#         )
#         # Crear un usuario para la fundación
#         self.user_fundacion = User.objects.create_user(
#             email="fundacion@example.com", password="securepassword123"
#         )
#         # Crear una fundación
#         self.fundacion = Fundacion.objects.create(
#             user=self.user_fundacion,
#             nombre="Fundación Ejemplo",
#             nit="123456789",
#             descripcion="Fundación para animales.",
#         )
#         # Crear una dirección
#         self.direccion = Direccion.objects.create(
#             direccion="Calle 123",
#             codigo_postal="12345",
#             localidad=None,  # Ajustar según el modelo de Localidad
#         )
#         # Crear un usuario para el dueño de la mascota
#         self.user_cliente = User.objects.create_user(
#             email="cliente@example.com", password="securepassword123"
#         )
#         # Crear una mascota
#         self.mascota = Mascota.objects.create(
#             user=self.user_cliente,
#             nombre="Rex",
#             sexo="M",
#             tipo="Perro",
#             raza="Labrador",
#             edad=3,
#             estado_salud="Saludable",
#             tamano="G",
#             peso=30.5,
#         )
#         # Datos base para publicaciones de adopción
#         self.publicacion_data = {
#             "fundacion": self.fundacion,
#             "mascota": self.mascota,
#             "titulo": "Adopción de Rex",
#             "descripcion": "Buscamos un hogar para Rex, un labrador cariñoso.",
#             "direccion": self.direccion,
#         }

#     def test_publicacion_adopcion_creation(self):
#         """Test para verificar que se puede crear una publicación de adopción correctamente"""
#         publicacion = PublicacionAdopcion.objects.create(**self.publicacion_data)
#         self.assertEqual(publicacion.fundacion, self.fundacion)
#         self.assertEqual(publicacion.mascota, self.mascota)
#         self.assertEqual(publicacion.titulo, "Adopción de Rex")
#         self.assertEqual(
#             publicacion.descripcion, "Buscamos un hogar para Rex, un labrador cariñoso."
#         )
#         self.assertEqual(publicacion.direccion, self.direccion)
#         self.assertIsNotNone(publicacion.fecha)  # Fecha autoasignada

#     def test_publicacion_adopcion_fundacion_obligatoria(self):
#         """Test para verificar que la fundación es obligatoria"""
#         self.publicacion_data["fundacion"] = None
#         with self.assertRaises(Exception):
#             PublicacionAdopcion.objects.create(**self.publicacion_data)

#     def test_publicacion_adopcion_mascota_obligatoria(self):
#         """Test para verificar que la mascota es obligatoria"""
#         self.publicacion_data["mascota"] = None
#         with self.assertRaises(Exception):
#             PublicacionAdopcion.objects.create(**self.publicacion_data)

#     def test_publicacion_adopcion_titulo_obligatorio(self):
#         """Test para verificar que el título es obligatorio"""
#         self.publicacion_data["titulo"] = ""
#         publicacion = PublicacionAdopcion(**self.publicacion_data)
#         with self.assertRaises(ValidationError):
#             publicacion.full_clean()  # Validación explícita

#     def test_publicacion_adopcion_descripcion_obligatoria(self):
#         """Test para verificar que la descripción es obligatoria"""
#         self.publicacion_data["descripcion"] = ""
#         publicacion = PublicacionAdopcion(**self.publicacion_data)
#         with self.assertRaises(ValidationError):
#             publicacion.full_clean()  # Validación explícita

#     def test_publicacion_adopcion_direccion_obligatoria(self):
#         """Test para verificar que la dirección es obligatoria"""
#         self.publicacion_data["direccion"] = None
#         with self.assertRaises(Exception):
#             PublicacionAdopcion.objects.create(**self.publicacion_data)

#     def test_publicacion_adopcion_str_method(self):
#         """Test para verificar que el método __str__ retorna el formato esperado"""
#         publicacion = PublicacionAdopcion.objects.create(**self.publicacion_data)
#         self.assertEqual(
#             str(publicacion), f"{publicacion.titulo} - {publicacion.mascota.nombre}"
#         )


# class SolicitudAdopcionModelTest(TestCase):
#     def setUp(self):
#         # Crear un usuario para el cliente
#         self.user_cliente = User.objects.create(
#             email="cliente@ejemplo.com", is_cliente=True
#         )
#         self.cliente = Cliente.objects.create(
#             user=self.user_cliente,
#             primer_nombre="Juan",
#             primer_apellido="Pérez",
#             cedula=1234567890,
#         )

#         # Crear un usuario para la fundación
#         self.user_fundacion = User.objects.create(
#             email="fundacion@ejemplo.com", is_fundacion=True
#         )
#         self.fundacion = Fundacion.objects.create(
#             user=self.user_fundacion,
#             nombre="Fundación Protectora",
#             nit="123456789",
#             descripcion="Fundación dedicada al cuidado de animales.",
#         )

#         # Crear una dirección
#         self.direccion = Direccion.objects.create(
#             direccion="Calle Falsa 123",
#             codigo_postal="12345",
#         )

#         # Crear una mascota
#         self.mascota = Mascota.objects.create(
#             user=self.user_fundacion,
#             nombre="Luna",
#             sexo="H",
#             tipo="Perro",
#             raza="Golden Retriever",
#             edad=3,
#             estado_salud="Saludable",
#             tamano="G",
#             peso=25.5,
#         )

#         # Crear una publicación de adopción con dirección asociada
#         self.publicacion = PublicacionAdopcion.objects.create(
#             fundacion=self.fundacion,
#             mascota=self.mascota,
#             titulo="Adopta a Luna",
#             descripcion="Golden Retriever cariñosa y juguetona busca un hogar.",
#             direccion=self.direccion,  # Asociar la dirección
#         )

#         # Datos para una solicitud de adopción
#         self.solicitud_data = {
#             "cliente": self.cliente,
#             "publicacion": self.publicacion,
#             "motivo": "Tengo experiencia con perros grandes y un hogar espacioso.",
#             "estado": "Pendiente",
#         }

#     def test_solicitud_adopcion_creation(self):
#         """Test para verificar que se puede crear una solicitud de adopción correctamente"""
#         solicitud = SolicitudAdopcion.objects.create(**self.solicitud_data)
#         self.assertEqual(solicitud.cliente, self.cliente)
#         self.assertEqual(solicitud.publicacion, self.publicacion)
#         self.assertEqual(
#             solicitud.motivo,
#             "Tengo experiencia con perros grandes y un hogar espacioso.",
#         )
#         self.assertEqual(solicitud.estado, "Pendiente")

#     def test_solicitud_adopcion_estado_invalido(self):
#         """Test para verificar que no se puede asignar un estado no válido"""
#         self.solicitud_data["estado"] = "Invalido"
#         with self.assertRaises(ValidationError):
#             solicitud = SolicitudAdopcion(**self.solicitud_data)
#             solicitud.full_clean()

#     def test_solicitud_adopcion_cliente_obligatorio(self):
#         """Test para verificar que el cliente es obligatorio"""
#         self.solicitud_data["cliente"] = None
#         with self.assertRaises(Exception):
#             SolicitudAdopcion.objects.create(**self.solicitud_data)

#     def test_solicitud_adopcion_publicacion_obligatoria(self):
#         """Test para verificar que la publicación es obligatoria"""
#         self.solicitud_data["publicacion"] = None
#         with self.assertRaises(Exception):
#             SolicitudAdopcion.objects.create(**self.solicitud_data)

#     def test_solicitud_adopcion_motivo_obligatorio(self):
#         """Test para verificar que el motivo es obligatorio"""
#         self.solicitud_data.pop("motivo")  # Elimina el motivo de los datos
#         with self.assertRaises(ValidationError):
#             solicitud = SolicitudAdopcion(**self.solicitud_data)
#             solicitud.full_clean()  # Esto valida los datos del modelo antes de guardar

#     def test_solicitud_adopcion_str_method(self):
#         """Test para verificar que el método __str__ retorna el formato esperado"""
#         solicitud = SolicitudAdopcion.objects.create(**self.solicitud_data)
#         self.assertEqual(
#             str(solicitud),
#             f"{self.cliente.primer_nombre} {self.cliente.primer_apellido} - {self.publicacion.titulo}",
#         )


# class MercadoPagoTestCase(TestCase):
#     def setUp(self):
#         """Configuración inicial para cada prueba"""
#         self.carrito = Carrito.objects.create(codigo="TEST123", pagado=False)

#     @patch("mercadopago.SDK.preference")
#     def test_create_preference(self, mock_preference):
#         """Verifica que se pueda crear una preferencia en Mercado Pago"""
#         mock_preference.return_value.create.return_value = {
#             "response": {
#                 "id": "1234567890",
#                 "init_point": "https://www.mercadopago.com/init_point_test",
#             }
#         }

#         data = {
#             "items": [
#                 {
#                     "title": "WHISKAS Sabor Pollo Sobres x 100gr",
#                     "quantity": 1,
#                     "unit_price": 4000,
#                     "currency_id": "COP",
#                 }
#             ]
#         }

#         response = self.client.post(
#             reverse("create_preference"),
#             json.dumps(data),
#             content_type="application/json",
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertIn("init_point", response.json())


class CarritoTestCase(TestCase):
    def setUp(self):
        """Configuración inicial para cada prueba"""
        self.client = APIClient()

        # Crear un carrito de prueba
        self.carrito = Carrito.objects.create(codigo="TEST123", pagado=False)

        # Crear un producto de prueba
        self.producto = Producto.objects.create(
            id=1, nombre="WHISKAS Sabor Pollo Sobres x 100gr", precio=4000
        )

        # Crear un item en el carrito
        self.item_carrito = ItemCarrito.objects.create(
            carrito=self.carrito, producto=self.producto, cantidad=1
        )

    def test_agregar_producto_al_carrito(self):
        """Verifica que un producto se agregue correctamente al carrito"""
        data = {
            "codigo": "TEST123",
            "id_producto": self.producto.id,
        }

        response = self.client.post(
            reverse("agregar_producto"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json())
        self.assertEqual(
            response.json()["message"], "Producto agregado al carrito exitosamente"
        )

    def test_producto_en_carrito(self):
        """Verifica que un producto está en el carrito"""
        response = self.client.get(
            reverse("producto_en_carrito")
            + f"?codigo=TEST123&id_producto={self.producto.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["producto_en_carrito"])

    def test_get_estado_carrito(self):
        """Verifica que se obtenga correctamente el estado del carrito"""
        response = self.client.get(
            reverse("get_estado_carrito") + f"?codigo_carrito=TEST123"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["codigo_carrito"], "TEST123")

    def test_update_cantidad_producto(self):
        """Verifica que se actualice la cantidad de un producto en el carrito"""
        data = {
            "codigo_carrito": "TEST123",
            "producto_id": self.producto.id,
            "cantidad": 5,
        }

        response = self.client.post(
            reverse("update_cantidad_producto"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.item_carrito.refresh_from_db()
        self.assertEqual(self.item_carrito.cantidad, 5)

    def test_remove_product_from_cart(self):
        """Verifica que un producto se elimine correctamente del carrito"""
        data = {"codigo_carrito": "TEST123", "producto_id": self.producto.id}

        response = self.client.post(
            reverse("remove_product_from_cart"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"].strip().rstrip("."),
            "Producto eliminado del carrito exitosamente",
        )

        # Verifica que el producto ya no existe en el carrito
        with self.assertRaises(ItemCarrito.DoesNotExist):
            ItemCarrito.objects.get(carrito=self.carrito, producto=self.producto)
