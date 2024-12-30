import random

from django.conf import settings
from django.core.mail import EmailMessage
from .models import User, OneTimePassword

def generateOTP():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp

def send_code_to_user(email):
    Subject = "One Time Password para la verificación por correo electrónico"
    otp_code = generateOTP()
    print(otp_code)
    user = User.objects.get(email=email)
    current_site = "Maki"
    email_body = f"Estimado usuario {user.email}, gracias por registrarte en {current_site}. Tu código de verificación es {otp_code}."
    from_email = settings.DEFAULT_FROM_EMAIL
    OneTimePassword.objects.create(user=user, code=otp_code)
    send_email = EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    send_email.send(fail_silently=True)


def send_normal_email(data):
    email = EmailMessage(
        subject = data['email_subject'],
        body = data['email_body'],
        from_email = settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()