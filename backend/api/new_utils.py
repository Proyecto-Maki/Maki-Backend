# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import ssl
import os
import random
from django.conf import settings
from .models import User, OneTimePassword
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import certifi
from rest_framework.response import Response


def generateOTP():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp

def date_format(date):
    return date.strftime('%d/%m/%Y %H:%M:%S')

def money_format(money):
    return "${:,.2f}".format(money)


def format_sexo_mascota(sexo):
    if sexo == 'M':
        return 'Macho'
    else:
        return 'Hembra'

def send_code_to_user(email):
    Subject = "OTP para la verificación por correo electrónico"
    otp_code = generateOTP()
    print(otp_code)
    user = User.objects.get(email=email)
    OneTimePassword.objects.create(user=user, code=otp_code)
    context = {"email": email, "otp_code": otp_code}

    html_message = render_to_string("email-otp.html", context=context)

    plain_message = strip_tags(html_message)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content=html_message,
    )

    message.add_bcc(settings.DEFAULT_FROM_EMAIL)

    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:

        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # sg.http.client.ca_certs = certifi.where()  # Configura el archivo de certificados
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
        }
    except Exception as e:
        print(str(e))
        return {
            "detail": "Error al enviar el correo electrónico",
            "error": str(e.body),
        }


def send_normal_email(data):

    Subject = data["email_subject"]
    email = data["email"]
    link = data["link"]
    to_email = data["to_email"]
    context = {"email": email, "link": link}
    html_message = render_to_string("email-pass-recovery.html", context=context)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=Subject,
        html_content=html_message,
    )

    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:

        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # sg.http.client.ca_certs = certifi.where()  # Configura el archivo de certificados
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
        }
    except Exception as e:
        print(str(e))
        return {
            "detail": "Error al enviar el correo electrónico",
            "error": str(e.body),
        }


def send_test_email():
    Subject = "Test 5 email"
    # email = "kelly.solano.1403@gmail.com"
    email = "apineross@unal.edu.co"
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content="<strong>Test email</strong>",
    )
    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:
        api_key = settings.SENDGRID_API_KEY
        sg = SendGridAPIClient(api_key=api_key)
        response = sg.send(message)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
            "body": response.body,
            "headers": response.headers,
        }

    except Exception as e:
        print(settings.SENDGRID_API_KEY)
        print(f"Este es el error {str(e)}")
        return e


def send_update_adoption_email(numero_solicitud, email, fecha, nuevo_estado, nombre_mascota, sexo_mascota, tipo_mascota, raza_mascota, edad_mascota, motivo, id_publicacion, nombre_fundacion, telefono_fundacion, direccion_fundacion, localidad_fundacion, email_fundacion):
    Subject = "Actualización de solicitud de adopción #{}".format(numero_solicitud)
    email = email
    context = {
        "numero_solicitud": numero_solicitud, 
        "email": email,
        "fecha": date_format(fecha),
        "nuevo_estado": nuevo_estado,
        "nombre_mascota": nombre_mascota,
        "sexo_mascota": format_sexo_mascota(sexo_mascota),
        "tipo_mascota": tipo_mascota,
        "raza_mascota": raza_mascota,
        "edad_mascota": edad_mascota,
        "motivo": motivo,
        "id_publicacion": id_publicacion,
        "nombre_fundacion": nombre_fundacion,
        "telefono_fundacion": telefono_fundacion,
        "direccion_fundacion": direccion_fundacion,
        "localidad_fundacion": localidad_fundacion,
        "email_fundacion": email_fundacion
    }
    html_message = render_to_string("email-update-adoption.html", context=context)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content=html_message,
    )

    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:

        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # sg.http.client.ca_certs = certifi.where()  # Configura el archivo de certificados
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
        }
    except Exception as e:
        print(str(e))
        return {
            "detail": "Error al enviar el correo electrónico",
            "error": str(e.body),
        }
    

def send_update_care_email(numero_solicitud, email, fecha, nuevo_estado, nombre_mascota, sexo_mascota, tipo_mascota, raza_mascota, edad_mascota, motivo, id_publicacion, nombre_fundacion, telefono_fundacion, direccion_fundacion, localidad_fundacion, email_fundacion):
    Subject = "Actualización de solicitud de cuidado #{}".format(numero_solicitud)
    email = email
    context = {
        "numero_solicitud": numero_solicitud, 
        "email": email,
        "fecha": date_format(fecha),
        "nuevo_estado": nuevo_estado,
        "nombre_mascota": nombre_mascota,
        "sexo_mascota": format_sexo_mascota(sexo_mascota),
        "tipo_mascota": tipo_mascota,
        "raza_mascota": raza_mascota,
        "edad_mascota": edad_mascota,
        "motivo": motivo,
        "id_publicacion": id_publicacion,
        "nombre_fundacion": nombre_fundacion,
        "telefono_fundacion": telefono_fundacion,
        "direccion_fundacion": direccion_fundacion,
        "localidad_fundacion": localidad_fundacion,
        "email_fundacion": email_fundacion
    }
    html_message = render_to_string("email-update-care.html", context=context)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content=html_message,
    )

    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:

        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # sg.http.client.ca_certs = certifi.where()  # Configura el archivo de certificados
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
        }
    except Exception as e:
        print(str(e))
        return {
            "detail": "Error al enviar el correo electrónico",
            "error": str(e.body),
        }
    

def send_cancel_care_email(numero_solicitud, email, fecha_solicitud, fecha_inicio, fecha_actualizacion, nombre_mascota, descripcion, costo, nombre_cuidador):
    Subject = "Cancelación de solicitud de cuidado #{}".format(numero_solicitud)
    email = email
    context = {
        "numero_solicitud": numero_solicitud, 
        "email": email,
        "fecha_solicitud": date_format(fecha_solicitud),
        "fecha_inicio": date_format(fecha_inicio),
        "fecha_actualizacion": date_format(fecha_actualizacion),
        "nombre_mascota": nombre_mascota,
        "descripcion": descripcion,
        "costo": costo,
        "nombre_cuidador": nombre_cuidador
    }
    html_message = render_to_string("email-cancel-care.html", context=context)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content=html_message,
    )

    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:

        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # sg.http.client.ca_certs = certifi.where()  # Configura el archivo de certificados
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
        }
    except Exception as e:
        print(str(e))
        return {
            "detail": "Error al enviar el correo electrónico",
            "error": str(e.body),
        }
    

def send_create_care_email(solicitud_id, email, mascota_nombre, fecha_solicitud, fecha_inicio, fecha_fin, horas_cuidado, is_cuidado_especial, descripcion, nombre_cuidador, estado, costo):
    Subject = "Creación de solicitud de cuidado #{}".format(solicitud_id)
    email = email

    horas = "0"
    if horas_cuidado == 24:
        horas = "Tiempo completo"
    else:
        horas = "{} horas".format(horas_cuidado)

    cuidado = "No"
    if is_cuidado_especial:
        cuidado = "Sí"


    context = {
        "solicitud_id": solicitud_id, 
        "mascota_nombre": mascota_nombre,
        "fecha_solicitud": date_format(fecha_solicitud),
        "fecha_inicio": date_format(fecha_inicio),
        "fecha_fin": date_format(fecha_fin),
        "horas_cuidado": horas,
        "is_cuidado_especial": cuidado,
        "descripcion": descripcion,
        "nombre_cuidador": nombre_cuidador,
        "estado": estado,
        "costo": money_format(costo)
    }
    html_message = render_to_string("email-create-care.html", context=context)

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content=html_message,
    )

    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
        ssl, "_create_unverified_context", None
    ):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:

        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        # sg.http.client.ca_certs = certifi.where()  # Configura el archivo de certificados
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
        }
    except Exception as e:
        print(str(e))
        return {
            "detail": "Error al enviar el correo electrónico",
            "error": str(e.body),
        }
    