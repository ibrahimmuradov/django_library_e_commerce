from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Book
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_delete, sender=Book)
def my_handler(sender, instance, **kwargs):
    get_author_email = instance.userauthor.email
    message = f'"{instance.name}" adlı kitabınız saytdan silindi'

    send_mail(
        'Kitabınız silindi',  # subject
        message,  # message
        'settings.EMAIL_HOST_USER',  # from mail
        [get_author_email],  # to mail
        fail_silently=False,
    )
