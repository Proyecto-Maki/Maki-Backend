
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



def generateOTP():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp

def send_code_to_user(email):
    Subject = "OTP para la verificación por correo electrónico"
    otp_code = generateOTP()
    print(otp_code)
    user = User.objects.get(email=email)
    OneTimePassword.objects.create(user=user, code=otp_code)
    context = {
        "email": email,
        "otp_code": otp_code
    }
    
    html_message = render_to_string('email-otp.html', context=context)

    plain_message = strip_tags(html_message)

    message = Mail(
        from_email= settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content=html_message)
    
    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
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
            "status_code": response.status_code
        }
    except Exception as e:
        print(str(e))
        return {
            "message": "Error al enviar el correo electrónico",
            "error": str(e.body)
        }


def send_normal_email(data):

    Subject = data['email_subject']
    email = data['email']
    link = data['link']
    to_email = data['to_email']
    context = {
        "email": email,
        "link": link
    }
    html_message = render_to_string('email-pass-recovery.html', context=context)

    message = Mail(
        from_email= settings.DEFAULT_FROM_EMAIL,
        to_email=to_email,
        subject=Subject,
        html_content=html_message)
    
    message.add_bcc(settings.DEFAULT_FROM_EMAIL)
    # os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
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
            "status_code": response.status_code
        }
    except Exception as e:
        print(str(e))
        return {
            "message": "Error al enviar el correo electrónico",
            "error": str(e.body)
        }
    

def send_test_email():
    Subject = "Test 3 email"
    email = "kelly.solano.1403@gmail.com"
    message = Mail(
        from_email= settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=Subject,
        html_content="<strong>Test email</strong>")
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:
        api_key = settings.SENDGRID_API_KEY
        sg = SendGridAPIClient(api_key=api_key)
        response = sg.send(message)
        return {
            "message": "Correo electrónico enviado con éxito",
            "status_code": response.status_code,
            "body": response.body,
            "headers": response.headers
        }

    except Exception as e:
        print(settings.SENDGRID_API_KEY)
        print(f"Este es el error {str(e)}")
        return {
            "message": "Error al enviar el correo electrónico",
            "error": str(e)  # Convert the exception to a string
        }
