from django.test import TestCase
from api.models import *
from django.db.utils import IntegrityError


class LocalidadModelTest(TestCase):
    def setUp(self):
        # Crear una instancia de Localidad para usar en los tests
        self.localidad = Localidad.objects.create(nombre="Medellín")

    def test_localidad_creation(self):
        """Test para verificar que una localidad se crea correctamente"""
        self.assertEqual(self.localidad.nombre, "Medellín")
        self.assertIsInstance(self.localidad, Localidad)

    def test_localidad_str_method(self):
        """Test para verificar que el método __str__ devuelve el formato correcto"""
        expected_str = f"{self.localidad.id} Medellín"
        self.assertEqual(str(self.localidad), expected_str)

    def test_localidad_nombre_max_length(self):
        """Test para verificar que el campo nombre respeta el max_length"""
        max_length = Localidad._meta.get_field("nombre").max_length
        self.assertEqual(max_length, 255)

    def test_crear_localidad_sin_nombre(self):
        """Test para verificar que no se puede crear una localidad sin nombre"""
        with self.assertRaises(IntegrityError):
            Localidad.objects.create(nombre="")


class DireccionModelTest(TestCase):
    def setUp(self):
        # Crear una instancia de Localidad para usar en los tests
        self.localidad = Localidad.objects.create(nombre="Medellín")
        # Crear una instancia de Direccion para usar en los tests
        self.direccion = Direccion.objects.create(
            direccion="Calle 123", codigo_postal="050001", localidad=self.localidad
        )

    def test_direccion_creation(self):
        """Test para verificar que se puede crear una dirección correctamente"""
        self.assertEqual(self.direccion.direccion, "Calle 123")
        self.assertEqual(self.direccion.codigo_postal, "050001")
        self.assertEqual(self.direccion.localidad, self.localidad)

    def test_direccion_str_method(self):
        """Test para verificar que el método __str__ devuelve el formato correcto"""
        expected_str = "Calle 123 Medellín"
        self.assertEqual(str(self.direccion), expected_str)

    def test_direccion_sin_localidad(self):
        """Test para verificar que no se puede crear una dirección sin localidad"""
        with self.assertRaises(IntegrityError):
            Direccion.objects.create(
                direccion="Calle sin localidad", codigo_postal="12345"
            )

    def test_direccion_codigo_postal_opcional(self):
        """Test para verificar que el código postal es opcional"""
        direccion_sin_cp = Direccion.objects.create(
            direccion="Calle sin CP", localidad=self.localidad
        )
        self.assertIsNone(direccion_sin_cp.codigo_postal)
        self.assertEqual(direccion_sin_cp.direccion, "Calle sin CP")


class UserManagerTest(TestCase):
    def setUp(self):
        # Configuración inicial
        self.user_data = {
            "email": "user@example.com",
            "password": "securepassword123",
            "is_cliente": True,
        }
        self.superuser_data = {
            "email": "admin@example.com",
            "password": "adminpassword123",
        }

    def test_create_user(self):
        """Test para verificar que se puede crear un usuario correctamente"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email(self):
        """Test para verificar que no se puede crear un usuario sin email"""
        with self.assertRaises(ValueError) as e:
            User.objects.create_user(email=None, password="password123")
        self.assertEqual(str(e.exception), "El email es obligatorio")

    def test_create_superuser(self):
        """Test para verificar que se puede crear un superusuario correctamente"""
        superuser = User.objects.create_superuser(**self.superuser_data)
        self.assertEqual(superuser.email, self.superuser_data["email"])
        self.assertTrue(superuser.check_password(self.superuser_data["password"]))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_without_is_staff_or_is_superuser(self):
        """Test para verificar que siempre se configuren is_staff e is_superuser en superusuarios"""
        superuser = User.objects.create_superuser(**self.superuser_data)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class UserModelTest(TestCase):
    def setUp(self):
        # Crear una instancia de Localidad para usar en Direccion
        self.localidad = Localidad.objects.create(nombre="Medellín")

        # Crear una instancia de Direccion válida
        self.direccion = Direccion.objects.create(
            direccion="Calle 123",
            codigo_postal="050001",
            localidad=self.localidad,
        )

        # Datos base para usuarios
        self.user_data = {
            "email": "user@example.com",
            "password": "securepassword123",
            "is_cliente": True,
            "direccion": self.direccion,
            "telefono": "1234567890",
            "saldo": 100.50,
        }

    def test_user_creation(self):
        """Test para verificar que se puede crear un usuario correctamente"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.direccion, self.direccion)
        self.assertEqual(user.telefono, "1234567890")
        self.assertEqual(user.saldo, 100.50)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_default_values(self):
        """Test para verificar los valores predeterminados del usuario"""
        user = User.objects.create_user(
            email="default@example.com", password="password123"
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_cliente)
        self.assertFalse(user.is_fundacion)
        self.assertFalse(user.is_verified)
        self.assertIsNone(user.direccion)
        self.assertEqual(user.saldo, 0.00)

    def test_user_str_method(self):
        """Test para verificar que el método __str__ devuelve el email del usuario"""
        user = User.objects.create_user(
            email="strtest@example.com", password="password123"
        )
        self.assertEqual(str(user), "strtest@example.com")

    def test_user_without_email(self):
        """Test para verificar que no se puede crear un usuario sin email"""
        with self.assertRaises(ValueError) as e:
            User.objects.create_user(email=None, password="password123")
        self.assertEqual(str(e.exception), "El email es obligatorio")

    def test_superuser_creation(self):
        """Test para verificar que se puede crear un superusuario correctamente"""
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword123"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


class ClienteModelTest(TestCase):
    def setUp(self):
        # Crear un usuario base para asociar con el cliente
        self.user = User.objects.create_user(
            email="cliente@example.com", password="securepassword123"
        )
        # Crear un cliente
        self.cliente = Cliente.objects.create(
            user=self.user,
            cedula=1234567890,
            primer_nombre="Juan",
            segundo_nombre="Carlos",
            primer_apellido="Pérez",
            segundo_apellido="Gómez",
        )

    def test_cliente_creation(self):
        """Test para verificar que un cliente se crea correctamente"""
        self.assertEqual(self.cliente.user, self.user)
        self.assertEqual(self.cliente.cedula, 1234567890)
        self.assertEqual(self.cliente.primer_nombre, "Juan")
        self.assertEqual(self.cliente.segundo_nombre, "Carlos")
        self.assertEqual(self.cliente.primer_apellido, "Pérez")
        self.assertEqual(self.cliente.segundo_apellido, "Gómez")

    def test_cliente_str_method(self):
        """Test para verificar que el método __str__ devuelve el formato correcto"""
        expected_str = "Juan Pérez"
        self.assertEqual(str(self.cliente), expected_str)

    def test_cliente_without_optional_fields(self):
        """Test para verificar que un cliente se puede crear con solo los campos obligatorios"""
        user = User.objects.create_user(
            email="simplecliente@example.com", password="password123"
        )
        cliente = Cliente.objects.create(user=user)
        self.assertIsNone(cliente.cedula)
        self.assertIsNone(cliente.primer_nombre)
        self.assertIsNone(cliente.segundo_nombre)
        self.assertIsNone(cliente.primer_apellido)
        self.assertIsNone(cliente.segundo_apellido)


class FundacionModelTest(TestCase):
    def setUp(self):
        # Crear un usuario base para asociar con la fundación
        self.user = User.objects.create_user(
            email="fundacion@example.com", password="securepassword123"
        )
        # Crear una fundación
        self.fundacion = Fundacion.objects.create(
            user=self.user,
            nombre="Fundación Amigos",
            nit="123456789-0",
            descripcion="Una fundación dedicada al bienestar animal.",
            premium=True,
        )

    def test_fundacion_creation(self):
        """Test para verificar que una fundación se crea correctamente"""
        self.assertEqual(self.fundacion.user, self.user)
        self.assertEqual(self.fundacion.nombre, "Fundación Amigos")
        self.assertEqual(self.fundacion.nit, "123456789-0")
        self.assertEqual(
            self.fundacion.descripcion, "Una fundación dedicada al bienestar animal."
        )
        self.assertTrue(self.fundacion.premium)

    def test_fundacion_str_method(self):
        """Test para verificar que el método __str__ devuelve el nombre de la fundación"""
        self.assertEqual(str(self.fundacion), "Fundación Amigos")

    def test_fundacion_without_optional_fields(self):
        """Test para verificar que una fundación se puede crear con solo los campos obligatorios"""
        user = User.objects.create_user(
            email="simplefundacion@example.com", password="password123"
        )
        fundacion = Fundacion.objects.create(user=user)
        self.assertIsNone(fundacion.nombre)
        self.assertIsNone(fundacion.nit)
        self.assertIsNone(fundacion.descripcion)
        self.assertFalse(fundacion.premium)


class MascotaModelTest(TestCase):
    def setUp(self):
        # Crear un usuario para asociar con las mascotas
        self.user = User.objects.create_user(
            email="user@example.com", password="securepassword123"
        )
        # Datos base para mascotas
        self.mascota_data = {
            "user": self.user,
            "nombre": "Rex",
            "sexo": "M",
            "tipo": "Perro",
            "raza": "Labrador",
            "edad": 3,
            "estado_salud": "Saludable",
            "tamano": "G",
            "peso": 30.5,
        }

    def test_mascota_creation(self):
        """Test para verificar que se puede crear una mascota correctamente"""
        mascota = Mascota.objects.create(**self.mascota_data)
        self.assertEqual(mascota.nombre, "Rex")
        self.assertEqual(mascota.sexo, "M")
        self.assertEqual(mascota.tipo, "Perro")
        self.assertEqual(mascota.raza, "Labrador")
        self.assertEqual(mascota.edad, 3)
        self.assertEqual(mascota.estado_salud, "Saludable")
        self.assertEqual(mascota.tamano, "G")
        self.assertEqual(mascota.peso, 30.5)

    def test_mascota_str_method(self):
        """Test para verificar que el método __str__ devuelve el formato correcto"""
        mascota = Mascota.objects.create(**self.mascota_data)
        expected_str = f"{mascota.id} Rex"
        self.assertEqual(str(mascota), expected_str)

    def test_mascota_invalid_sexo(self):
        """Test para verificar que no se puede asignar un sexo no válido"""
        invalid_data = self.mascota_data.copy()
        invalid_data["sexo"] = "X"
        mascota = Mascota(**invalid_data)
        with self.assertRaises(ValidationError):
            mascota.full_clean()

    def test_mascota_invalid_estado_salud(self):
        """Test para verificar que no se puede asignar un estado de salud no válido"""
        invalid_data = self.mascota_data.copy()
        invalid_data["estado_salud"] = "Desconocido"
        mascota = Mascota(**invalid_data)
        with self.assertRaises(ValidationError):
            mascota.full_clean()

    def test_mascota_imagen_opcional(self):
        """Test para verificar que la imagen es opcional"""
        mascota = Mascota.objects.create(**self.mascota_data)
        self.assertIsNone(mascota.imagen)

    def test_mascota_invalid_tamano(self):
        """Test para verificar que no se puede asignar un tamaño no válido"""
        invalid_data = self.mascota_data.copy()
        invalid_data["tamano"] = "X"
        mascota = Mascota(**invalid_data)
        with self.assertRaises(ValidationError):
            mascota.full_clean()


class PadecimientoModelTest(TestCase):
    def setUp(self):
        # Crear un usuario para asociar con la mascota
        self.user = User.objects.create_user(
            email="user@example.com", password="securepassword123"
        )
        # Crear una mascota para asociar con los padecimientos
        self.mascota = Mascota.objects.create(
            user=self.user,
            nombre="Rex",
            sexo="M",
            tipo="Perro",
            raza="Labrador",
            edad=3,
            estado_salud="Saludable",
            tamano="G",
            peso=30.5,
        )
        # Datos base para padecimientos
        self.padecimiento_data = {
            "mascota": self.mascota,
            "padecimiento": "Parvovirus",
        }

    def test_padecimiento_creation(self):
        """Test para verificar que se puede crear un padecimiento correctamente"""
        padecimiento = Padecimiento.objects.create(**self.padecimiento_data)
        self.assertEqual(padecimiento.mascota, self.mascota)
        self.assertEqual(padecimiento.padecimiento, "Parvovirus")

    def test_padecimiento_str_method(self):
        """Test para verificar que el método __str__ devuelve el formato correcto"""
        padecimiento = Padecimiento.objects.create(**self.padecimiento_data)
        expected_str = f"{self.mascota.nombre} - Parvovirus"
        self.assertEqual(str(padecimiento), expected_str)

    def test_padecimiento_sin_padecimiento(self):
        """Test para verificar que no se puede crear un padecimiento sin descripción"""
        invalid_data = self.padecimiento_data.copy()
        invalid_data["padecimiento"] = ""
        padecimiento = Padecimiento(**invalid_data)
        with self.assertRaises(ValidationError):
            padecimiento.full_clean()

    def test_padecimiento_sin_mascota(self):
        """Test para verificar que no se puede crear un padecimiento sin mascota"""
        invalid_data = self.padecimiento_data.copy()
        invalid_data["mascota"] = None
        with self.assertRaises(Exception):
            Padecimiento.objects.create(**invalid_data)


from django.test import TestCase
from api.models import Producto


class ProductoModelTest(TestCase):
    def setUp(self):
        # Datos base para los productos
        self.producto_data = {
            "nombre": "Croquetas de pollo",
            "descripcion": "Deliciosas croquetas de pollo para mascotas.",
            "precio": 49.99,
            "stock": 10,
            "categoria": "Alimentos",
            "ingredientes": "Pollo, cereales, vitaminas",
        }

    def test_producto_creation(self):
        """Test para verificar que se puede crear un producto correctamente"""
        producto = Producto.objects.create(**self.producto_data)
        self.assertEqual(producto.nombre, "Croquetas de pollo")
        self.assertEqual(
            producto.descripcion, "Deliciosas croquetas de pollo para mascotas."
        )
        self.assertEqual(producto.precio, 49.99)
        self.assertEqual(producto.stock, 10)
        self.assertEqual(producto.categoria, "Alimentos")
        self.assertEqual(producto.ingredientes, "Pollo, cereales, vitaminas")

    def test_producto_slug_autogeneration(self):
        """Test para verificar que el slug se genera automáticamente si no se proporciona"""
        producto = Producto.objects.create(**self.producto_data)
        self.assertEqual(producto.slug, "croquetas-de-pollo")

    def test_producto_slug_custom(self):
        """Test para verificar que el slug no se sobrescribe si se proporciona uno personalizado"""
        self.producto_data["slug"] = "custom-slug"
        producto = Producto.objects.create(**self.producto_data)
        self.assertEqual(producto.slug, "custom-slug")

    def test_producto_str_method(self):
        """Test para verificar que el método __str__ devuelve el nombre del producto"""
        producto = Producto.objects.create(**self.producto_data)
        self.assertEqual(str(producto), "Croquetas de pollo")

    def test_producto_imagen_opcional(self):
        """Test para verificar que la imagen es un campo opcional"""
        producto = Producto.objects.create(**self.producto_data)
        self.assertIsNone(producto.imagen)

    def test_producto_precio_por_defecto(self):
        """Test para verificar que el precio por defecto es 0.00"""
        self.producto_data.pop("precio")  # Remover el precio de los datos iniciales
        producto = Producto.objects.create(**self.producto_data)
        self.assertEqual(producto.precio, 0.00)

    def test_producto_stock_por_defecto(self):
        """Test para verificar que el stock por defecto es 0"""
        self.producto_data.pop("stock")  # Remover el stock de los datos iniciales
        producto = Producto.objects.create(**self.producto_data)
        self.assertEqual(producto.stock, 0)
