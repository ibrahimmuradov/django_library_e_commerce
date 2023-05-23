from django.contrib import admin
from .models import Category, Book, BookImage, Comment, Contact, RentBook, Queue, Cart, Order, OrderItem, OrderInfo
from authoraccount.models import Users

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    search_fields = ("name", "code")

admin.site.register(Category, CategoryAdmin)

class BookAdmin(admin.ModelAdmin):
    list_display = ("name", "release_date", "view_count", "wishlist_count")

admin.site.register(Book, BookAdmin)

class BookImg(admin.ModelAdmin):
    list_display = ("book", "image")

admin.site.register(BookImage, BookImg)

class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email")

admin.site.register(Contact, ContactAdmin)

class RentBookAdmin(admin.ModelAdmin):
    list_display = ("user", "book")

admin.site.register(RentBook, RentBookAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "author")

admin.site.register(Comment, CommentAdmin)

class QueueAdmin(admin.ModelAdmin):
    list_display = ("user", "book")

admin.site.register(Queue, QueueAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "book")

admin.site.register(Cart, CartAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("book", "quantity")

admin.site.register(OrderItem, OrderItemAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ("user",)

admin.site.register(Order, OrderAdmin)

class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ("user", "book")

admin.site.register(OrderInfo, OrderInfoAdmin)