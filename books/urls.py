from django.urls import path
from . import views

app_name = "books"
handler404 = 'books.views.handler404'

urlpatterns = [
    path("", views.index_view, name="index"),
    path("about/", views.about_view, name="about"),
    path("shop/", views.shop_view, name="shop"),
    path("cart/", views.cart_view, name="cart"),
    path("detail/<int:id>/", views.detail_view, name="detail"),
    path("delcomment/", views.delcomment_view, name="delcomment"),
    path("wish/", views.wish_view, name="wish"),
    path("queue/", views.queue_view, name="queue"),
    path("createcart/", views.book_cart_create_view, name="createcart"),
    path("contact/", views.contact_view, name="contact"),
    path("base/", views.base_view, name="base"),
]
