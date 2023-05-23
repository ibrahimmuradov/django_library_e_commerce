from django.contrib import admin
from .models import *


class AuthorAdmin(admin.ModelAdmin):
    list_display = ("username", "email")

admin.site.register(Author, AuthorAdmin)

