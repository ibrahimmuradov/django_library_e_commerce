from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("activate/<slug>/", views.activate_account_code_view, name="activate"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.password_change_view, name="change-password"),
    path("reset/", views.reset_password_view, name="reset"),
    path("reset-complete/<slug>/", views.reset_password_complete_view, name="reset-complete"),
    path("info/", views.info_view, name="info"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("delwish/", views.delwish_view, name="delwish"),
    path("queue/", views.queue_view, name="queue"),
    path("delqueue/", views.delqueue_view, name="delqueue"),
    path("cart/", views.cart_view, name="cart"),
    path("delcart/", views.delete_cart_view, name="delcart"),
    path("payment/<redirectlink>/", views.payment_view, name="payment"),
]
