from django.urls import path
from . import views

app_name = "author"

urlpatterns = [
    path("statics/", views.statics_view, name="statics"),
    path("list/", views.list_view, name="list"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("activate/<slug>/", views.activate_account_code_view, name="activate"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.password_change_view, name="change-password"),
    path("reset/", views.reset_password_view, name="reset"),
    path("reset-complete/<slug>/", views.reset_password_complete_view, name="reset-complete"),
    path("info/", views.info_view, name="info"),
    path("book-create/", views.book_create_view, name="book-create"),
    path("book-list/", views.book_list_view, name="book-list"),
    path("book-update/<int:id>/", views.book_update_view, name="book-update"),
    path("book-delete/<int:id>/", views.book_delete_view, name="book-delete"),
]
