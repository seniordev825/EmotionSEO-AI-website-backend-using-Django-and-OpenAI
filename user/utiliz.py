import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def send_otp_email(email, otp):
    subject = 'Tu codigo de validación'
    message = f'Tu codigo de validación is: {otp}'
    from_email = 'hola@emotionseo.ai'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)