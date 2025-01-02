# import random
# import os.path
# from django.conf import settings
# # from django.core.mail import EmailMessage, EmailMultiAlternatives
# from .models import User, OneTimePassword
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags

# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from google.oauth2 import service_account
# import base64
# from email.message import EmailMessage
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# def generateOTP():
#     otp = ""
#     for i in range(6):
#         otp += str(random.randint(0, 9))
#     return otp

# def send_code_to_user(email):

#     flow = InstalledAppFlow.from_client_secrets_file(settings.CREDENTIALS_FILE_PATH, SCOPES)
#     creds = flow.run_local_server()
#     service = build('gmail', 'v1', credentials=creds)

#     Subject = "OTP para la verificación por correo electrónico"
#     otp_code = generateOTP()
#     print(otp_code)
#     user = User.objects.get(email=email)
#     # current_site = "Maki"
#     # email_body = f"Estimado usuario {user.email}, gracias por registrarte en {current_site}. Tu código de verificación es {otp_code}."
#     # from_email = settings.DEFAULT_FROM_EMAIL
#     OneTimePassword.objects.create(user=user, code=otp_code)
#     # send_email = EmailMessage(subject=Subject, body=email_body, from_email=from_email, to=[email])
#     # send_email.send(fail_silently=True)
#     context = {
#         "email": email,
#         "otp_code": otp_code
#     }
    
#     html_message = render_to_string('email-otp.html', context=context)

#     plain_message = strip_tags(html_message)
#     # message = EmailMultiAlternatives(
#     #     subject=Subject,
#     #     body=plain_message,
#     #     from_email=settings.DEFAULT_FROM_EMAIL,
#     #     to=[email]
#     # )

#     # message.attach_alternative(html_message, "text/html")
#     # message.send()
#     part1 = MIMEText(plain_message, 'plain')
#     part2 = MIMEText(html_message, 'html')
#     message = MIMEMultipart('alternative')
#     message.attach(part1)
#     message.attach(part2)

#     message['to'] = email
#     message['from'] = settings.DEFAULT_FROM_EMAIL
#     message['subject'] = Subject
#     create_message = {'raw': base64.urlsafe_b64encode(message.as_string().as_bytes()).decode()}
#     try:
#         message = service.users().messages().send(userId='me', body=create_message).execute()
#         print('Se envio el mensaje')
#         return {'info-message': message,
#                 'message': 'Se envio el mensaje'}
#     except HttpError as error:
#         print('Ocurrio un error: %s' % error)
#         message = None
#         return {'error': error,
#                 'message': 'Ocurrio un error'}
    


# def send_normal_email(data):
#     # email = EmailMessage(
#     #     subject = data['email_subject'],
#     #     body = data['email_body'],
#     #     from_email = settings.EMAIL_HOST_USER,
#     #     to=[data['to_email']]
#     # )
#     # email.send()


#     # Subject = data['email_subject']
#     # email = data['email']
#     # link = data['link']
#     # to_email = data['to_email']
#     # context = {
#     #     'email': email,
#     #     'link': link
#     # }
#     # html_message = render_to_string('email-pass-recovery.html', context=context)
#     # plain_message = strip_tags(html_message)
#     # message = EmailMultiAlternatives(
#     #     subject=Subject,
#     #     body=plain_message,
#     #     from_email=settings.DEFAULT_FROM_EMAIL,
#     #     to=[to_email]
#     # )
#     # message.attach_alternative(html_message, "text/html")
#     # message.send()
#     None