import random

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from .models import User, OneTimePassword
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
    # current_site = "Maki"
    # email_body = f"Estimado usuario {user.email}, gracias por registrarte en {current_site}. Tu código de verificación es {otp_code}."
    # from_email = settings.DEFAULT_FROM_EMAIL
    OneTimePassword.objects.create(user=user, code=otp_code)
    # send_email = EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
    # send_email.send(fail_silently=True)
    context = {
        "email": email,
        "otp_code": otp_code
    }
    
    html_message = render_to_string('email-otp.html', context=context)

    plain_message = strip_tags(html_message)
    message = EmailMultiAlternatives(
        subject=Subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )

    message.attach_alternative(html_message, "text/html")
    message.send()


def send_normal_email(data):
    email = EmailMessage(
        subject = data['email_subject'],
        body = data['email_body'],
        from_email = settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()