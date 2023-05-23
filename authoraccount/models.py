from django.db import models
from ckeditor.fields import RichTextField
from services.generator import CodeGenerator
from services.uploader import Uploader
from django.contrib.auth import get_user_model
from services.mixin import DateMixin

Users = get_user_model()

class Author(DateMixin):
    username = models.OneToOneField(Users, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    surname = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=320, blank=True, null=True)
    earning = models.FloatField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    bio = RichTextField(blank=True, null=True)
    photo = models.ImageField(upload_to=Uploader.upload_image_author, blank=True, null=True)
    activation_code = models.CharField(max_length=200, blank=True, null=True)
    email_verification_code = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return str(self.username)

    def save(self, *args, **kwargs):
        self.slug = CodeGenerator.create_activation_link_code(
            size=20, model_=Author
        )
        return super().save(*args, **kwargs)

