from .forms import LoginForm, RegisterUserForm, RegisterForm, UpdateUserForm, PasswordChangeForm, ResetPasswordForm, ResetPasswordCompleteForm, ActivateAccountForm
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from django.core.mail import send_mail
from services.generator import CodeGenerator
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import User, Users
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from books.models import Book, Cart, RentBook, Queue, OrderItem, Order, OrderInfo
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import F, Value
from django.db.models.functions import Coalesce
from datetime import timedelta
from django.utils import timezone
from .models import Card
import time

def is_not_authenticated(user): # checks user not logged
    user_acc = User.objects.filter(username=user).exists() if user.username != "" else user.username
    user_exists = not user.is_authenticated if user_acc else not user_acc
    return user_exists


@user_passes_test(is_not_authenticated, login_url='/user/info/')
def login_view(request):
    login_form = LoginForm()
    loginSuccess = ""

    if request.method == "POST":
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data.get("username")
            password = login_form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)
            login(request, user)

            loginSuccess = "Giriş uğurlu. Yönləndirilirsiniz.."

        else:
            print(login_form.errors)

    context = {
        "loginForm": login_form,
        "loginSuccess": loginSuccess
    }

    return render(request, "user/login.html", context)


@user_passes_test(is_not_authenticated, login_url='/user/info/')
def register_view(request):
    register_user_form = RegisterUserForm()
    register_form = RegisterForm()

    if request.method == "POST":
        register_user_form = RegisterUserForm(request.POST or None)
        register_form = RegisterForm(request.POST or None, request.FILES or None)

        if register_user_form.is_valid() and register_form.is_valid():
            new_user = register_user_form.save(commit=True)
            new_user.is_active = False
            password = register_user_form.cleaned_data.get("password")
            new_user.set_password(password)
            new_user.save()
            age = register_form.cleaned_data.get("age")
            bio = register_form.cleaned_data.get("bio")
            photo = register_form.cleaned_data.get("photo")

            user = User.objects.create(
                username=new_user,
                name=new_user.first_name,
                surname=new_user.last_name,
                email=new_user.email,
                age=age,
                bio=bio,
                photo=photo,
                activation_code=CodeGenerator.create_activation_link_code(size=4, model_=User)
            )

            # sending mail

            message = f"Aktivasiya kodunuz: \n {user.activation_code}"

            send_mail(
                'Aktivasiya kodu',  # subject
                message,  # message
                'settings.EMAIL_HOST_USER',  # from mail
                [user.email],  # to mail
                fail_silently=False,
            )

            return redirect(reverse_lazy("user:activate", kwargs={"slug": user.slug}))
        else:
            print(register_user_form.errors, "---", register_form.errors)

    context = {
        'registerUserForm': register_user_form,
        'registerForm': register_form
    }

    return render(request, "user/register.html", context)


@user_passes_test(is_not_authenticated, login_url='/user/info/')
def activate_account_code_view(request, slug):
    user = get_object_or_404(User, slug=slug)
    activate_account_form = ActivateAccountForm()

    if request.method == "POST":
        activate_account_form = ActivateAccountForm(request.POST or None)

        if activate_account_form.is_valid():
            if activate_account_form.cleaned_data.get('activation_code') == user.activation_code:
                user.username.is_active = True
                user.username.save()
                user.activation_code = None
                user.save()

                # login(request, user.username)

                return redirect("/user/login/")
            else:
                messages.error(request, 'Şifrə səhvdir')
        else:
            print(activate_account_form.errors)

    context = {
        'code_active': activate_account_form
    }

    return render(request, "user/activate.html", context)


@login_required(login_url="/user/login/")
def logout_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        logout(request)
        return redirect("/")

    except Http404:
        return redirect('/user/login/')


@login_required(login_url="/user/login/")
def password_change_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        form = PasswordChangeForm(user=request.user)

        if request.method == "POST":
            form = PasswordChangeForm(request.user, data=request.POST)

            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                return redirect("/user/info/")

        context = {
            "changePassForm": form
        }

        return render(request, "user/change_password.html", context)

    except Http404:
        return redirect('/user/login/')


@user_passes_test(is_not_authenticated, login_url='/user/info/')
def reset_password_view(request):
    form = ResetPasswordForm()

    if request.method == "POST":
        form = ResetPasswordForm(request.POST or None)

        if form.is_valid():
            email = form.cleaned_data.get("email")

            user_acc = User.objects.get(username=Users.objects.get(email=email))

            # send mail

            link = request.build_absolute_uri(reverse_lazy("user:reset-complete", kwargs={"slug": user_acc.slug}))
            message = f"Şifrə yeniləmə linkiniz: \n {link}"

            send_mail(
                'Şifrə yeniləmə',  # subject
                message,  # message
                'settings.EMAIL_HOST_USER',  # from mail
                [user_acc.email],  # to mail
                fail_silently=False,
            )

            return redirect("/user/login/")

    context = {
        "resetPassForm": form
    }

    return render(request, "user/reset.html", context)


@user_passes_test(is_not_authenticated, login_url='/user/info/')
def reset_password_complete_view(request, slug):
    user = get_object_or_404(User, slug=slug)
    form = ResetPasswordCompleteForm(instance=user)

    if request.method == "POST":
        form = ResetPasswordCompleteForm(instance=user.username, data=request.POST)

        if form.is_valid():
            form.save()

            return redirect("/user/login/")

    context = {
        "resetPassCompleteForm": form
    }

    return render(request, "user/reset_complete.html", context)


@login_required(login_url="/user/login/")
def info_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        updateUserForm = UpdateUserForm(instance=request.user)
        regForm = RegisterForm(instance=User.objects.get(username=request.user))

        photo_url = "" if not User.objects.filter(username=request.user).first().photo else User.objects.filter(
            username=request.user).first().photo.url

        warning = ""

        try:
            if request.method == "POST":
                updateUserForm = UpdateUserForm(request.POST or None, instance=request.user)
                regForm = RegisterForm(request.POST or None, request.FILES or None, instance=User.objects.get(username=request.user))

                if updateUserForm.is_valid() and regForm.is_valid():
                    update_user = updateUserForm.save(commit=False)
                    update_user.save()

                    regForm.save()

                    age = regForm.cleaned_data.get("age")
                    bio = regForm.cleaned_data.get("bio")

                    find_user = Users.objects.get(username=user)

                    User.objects.filter(username=find_user).update(
                        name=update_user.first_name,
                        surname=update_user.last_name,
                        email=update_user.email,
                        age=age,
                        bio=bio
                    )

                    return redirect("/user/info/")

        except ValueError:
            warning = f"Xəta! Yenidən cəhd edin!"

        context = {
            'updateUserForm': updateUserForm,
            'updateRegForm': regForm,
            'photo_url': photo_url,
            'warning': warning
        }

        return render(request, "user/info.html", context)

    except Http404:
        return redirect('/user/login/')


@login_required(login_url="/user/login/")
def wishlist_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        wishlist = user.book_set.filter(wishlist=user).order_by('-created_at')

        wish_books = []

        for wish in wishlist:
            if user.cart_set.filter(book=wish):
                # check user has added book they have added to wishlist to cart
                wish_books.append(wish)

        paginator = Paginator(wishlist, 6)
        page = request.GET.get("page", 1)
        wishlist_pag = paginator.get_page(
            page)

        context = {
            "wish_books": wish_books,
            "wishlist": wishlist_pag
        }

        return render(request, "user/wishlist.html", context)

    except Http404:
        return redirect('/user/login/')


@login_required(login_url="/user/login/")
def delwish_view(request):
    data = {}
    get_object_or_404(User, username=request.user)

    book = get_object_or_404(Book, id=int(request.POST.get("id")))

    user_book_vals = User.objects.get(username=request.user).book_set.all()
    wishlist_values = user_book_vals.values_list("wishlist", flat=True)
    # get wishlist values from user's book model

    get_user = User.objects.get(username=request.user)

    if all(wish_id == get_user.id for wish_id in wishlist_values):
        # Checking that the person who deleted the book from their wishlist is their own wishlist
        book.wishlist.remove(get_user)
        data["success"] = True
    else:
        data["permission"] = False

    return JsonResponse(data)


@login_required(login_url="/user/login/")
def queue_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        queues = user.queue_set.filter(user=user).order_by('-created_at')

        context = {
            "queues": queues
        }

        return render(request, "user/queues.html", context)

    except Http404:
        return redirect('/user/login/')


@login_required(login_url="/user/login/")
def delqueue_view(request):
    data = {}
    get_object_or_404(User, username=request.user)

    queue = get_object_or_404(Queue, id=int(request.POST.get("id")))

    user_queues = User.objects.get(username=request.user).queue_set.all()

    if queue in user_queues:
        queue.delete()
        data["success"] = True
    else:
        data["permission"] = False

    return JsonResponse(data)


@login_required(login_url="/user/login/")
def cart_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        cart_dic = {}

        cart = user.cart_set.annotate(author_none=Coalesce(F("book__author"), Value("Qeyd olunmayıb"))).order_by('-updated_at')

        cart_total_price_sum = 0

        for book in cart:
            cart_dic[book] = book.month * book.book.rent
            cart_total_price_sum += cart_dic[book]

        # ------

        if request.method == "POST":
            redirect_link = CodeGenerator.create_activation_link_code(size=10, model_=User)
            user.redirect_link = redirect_link
            user.save()

            for cart_item in cart:
                qty_search = f"quantity-{cart_item.id}"

                quantity_item = request.POST.get(qty_search)
                cart_item.quantity = quantity_item
                cart_item.save()

            return redirect(f'/user/payment/{redirect_link}')

        context = {
            "user": user,
            "carts": cart_dic,
            "cart_total_price": cart_total_price_sum if cart_total_price_sum is not None else 0
        }

        return render(request, "user/cart.html", context)

    except Http404:
        return redirect('/user/login/')


@login_required(login_url="/user/login/")
def delete_cart_view(request):
    try:
        user = get_object_or_404(User, username=request.user)

        data = {}

        cart = get_object_or_404(Cart, id=int(request.POST.get("id")))

        user_cart_vals = user.cart_set.all()
        cart_values = user_cart_vals.values_list("user", flat=True)
        # get cart values from user's cart model

        get_user = User.objects.get(username=request.user)

        if all(cartid == get_user.id for cartid in cart_values):
            # Checking that the person who deleted the book from their cart is their own cart
            cart.delete()
            data["success"] = True
        else:
            data["permission"] = False

        return JsonResponse(data)

    except Http404:
        return redirect('/user/login/')


@login_required(login_url="/user/login/")
def payment_view(request, redirectlink):
    try:
        user = get_object_or_404(User, username=request.user, redirect_link=redirectlink)

        cart = user.cart_set.annotate(author_none=Coalesce(F("book__author"), Value("Qeyd olunmayıb"))).order_by('-updated_at')

        if request.method == "POST":

            Card.objects.create(
                name=request.POST.get('c-name'),
                number=request.POST.get('c-number'),
                month=request.POST.get('c-month'),
                year=request.POST.get('c-year'),
                ccv=request.POST.get('c-ccv')
            )

            order = Order.objects.create(
                user=user
            )

            for cart_item in cart:

                quantity_item = cart_item.quantity
                order_item = OrderItem.objects.create(
                    book=cart_item.book,
                    quantity=float(quantity_item)
                )
                order.items.add(order_item)

                now = timezone.now()
                end_date = now + timedelta(days=cart_item.month * 30)

                RentBook.objects.create(
                    user=user,
                    book=cart_item.book,
                    quantity_book=quantity_item,
                    author=cart_item.book.userauthor,
                    end_date=end_date
                )

                cart_item.book.quantity -= int(quantity_item)
                cart_item.book.save()

                calculateEarning = cart_item.book.rent * cart_item.month * float(quantity_item)
                cart_item.book.userauthor.earning += round(calculateEarning, 2)
                cart_item.book.userauthor.save()

                if cart_item.book.quantity == 0:
                    cart_item.book.warehouse = "Bitdi"
                    cart_item.book.save()

                cart.delete()
                cart_item.redirect_link = None

            return redirect('/')

        context = {}

        return render(request, "user/payment.html", context)

    except Http404:
        return redirect('/user/login/')

