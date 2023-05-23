from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from services.generator import CodeGenerator
from services.slugify import slugify
from services.uploader import Uploader
from mptt.models import MPTTModel, TreeForeignKey
from authoraccount.models import Author
from useraccount.models import User
from django.db.models import Q
from services.mixin import DateMixin, SlugMixin
import json

Users = get_user_model()

warehouse = (
    ("Mövcuddur", "Mövcuddur"),
    ("Bitdi", "Bitdi"),
    ("Gözlənilir", "Gözlənilir")
)

status = (
    ("Aktiv", "Aktiv"),
    ("Deaktiv", "Deaktiv")
)

class Category(DateMixin, SlugMixin, MPTTModel):
    name = models.CharField(max_length=300, blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        self.code = CodeGenerator.create_activation_link_code(size=20, model_=Category)
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @property
    def product_count(self):
        return Book.object.filter(
            Q(category_id=self.id) | Q(category__parent_id=self.id)
        ).count()


class Book(DateMixin, SlugMixin):
    userauthor = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    summary = RichTextField(blank=True, null=True)
    author = models.CharField(max_length=300, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    release_date = models.PositiveIntegerField(blank=True, null=True)
    rent = models.FloatField(blank=True, null=True)
    r_month = models.CharField(max_length=2500, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    warehouse = models.CharField(max_length=200, choices=warehouse, blank=True, null=True)
    wishlist = models.ManyToManyField(User, blank=True, null=True)
    status = models.CharField(max_length=200, choices=status, blank=True, null=True)
    view_count = models.PositiveIntegerField(blank=True, null=True)
    wishlist_count = models.PositiveIntegerField(blank=True, null=True)

    def set_list_field(self, value):
        self.r_month = json.dumps(value)

    def get_list_field(self):
        return json.loads(self.r_month)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def save(self, *args, **kwargs):
        self.code = CodeGenerator.create_activation_link_code(size=20, model_=Book)
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class BookImage(DateMixin):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to=Uploader.upload_image_book, blank=True, null=True)

    def __str__(self):
        return self.book.name

    class Meta:
        ordering = ("-created_at", )
        verbose_name = "Book Image"
        verbose_name_plural = "Book Images"


class Comment(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} --- {self.book.name}'

    class Meta:
        ordering = ("-created_at", )
        verbose_name = "Comment"
        verbose_name_plural = "Comments"


class Contact(DateMixin):
    name = models.CharField(max_length=300, blank=True, null=True)
    email = models.CharField(max_length=320, blank=True, null=True)
    message = RichTextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-created_at", )
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"


class Queue(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.user.name} --- {self.book.name}'

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Queue"
        verbose_name_plural = "Queues"


class RentBook(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)
    quantity_book = models.PositiveIntegerField(blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.book.name

    class Meta:
        ordering = ("-created_at", )
        verbose_name = "Rent Book"
        verbose_name_plural = "Rent Books"


class Cart(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    month = models.PositiveIntegerField(null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} --- {self.book.name}"

class OrderItem(DateMixin):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.book.name

class Order(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    items = models.ManyToManyField(OrderItem, blank=True, null=True)

    def __str__(self):
        return self.user.name


class OrderInfo(DateMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    bookuserauthor = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True, null=True)
    authorearning = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.user} -- {self.user}'

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Order Info"
        verbose_name_plural = "Order Infos"
