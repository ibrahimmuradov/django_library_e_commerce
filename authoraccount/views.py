from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import LoginForm, RegisterUserForm, UpdateUserForm, RegisterForm, ResetPasswordForm, ResetPasswordCompleteForm, BookCreateForm, BookImageCreateForm, ActivateAccountForm
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from services.generator import CodeGenerator
from django.urls import reverse_lazy
from django.db.models import F, Q, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from books.models import Book, BookImage, RentBook
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib import messages
from useraccount.models import User

def is_not_authenticated(user): # checks user not logged
    author_acc = Author.objects.filter(username=user).exists() if user.username != "" else user.username
    user_exists = not user.is_authenticated if author_acc else not author_acc
    return user_exists


@login_required(login_url="/author/login/")
def statics_view(request):
    try:
        author = get_object_or_404(Author, username=request.user)

        rentBook = author.rentbook_set.all()

        wishlist_books = author.book_set.filter(wishlist_count__gte=1).order_by('-wishlist_count')[:5] # author's most wishlisted books

        view_c = author.book_set.all().values('view_count')
        wishlist_c = author.book_set.all().values('wishlist_count')
        rent_book_c = rentBook.all().count()

        total_view_count = 0
        for view in view_c:
            total_view_count += view['view_count']

        total_wishlist_count = 0
        for wish in wishlist_c:
            total_wishlist_count += wish['wishlist_count']

        context = {
            "author": author,
            "rent_book": rentBook,
            "rent_book_c": rent_book_c,
            "total_view": total_view_count,
            "total_wishlist": total_wishlist_count,
            "wishlist_books": wishlist_books
        }

        return render(request, "author/index.html", context)

    except Http404:
        return redirect('/author/login/')


@login_required(login_url="/author/login/")
def list_view(request):
    try:
        user = get_object_or_404(Author, username=request.user)

        return render(request, "author/list.html", {})

    except Http404:
        return redirect('/author/login/')


@user_passes_test(is_not_authenticated, login_url='/author/info/')
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

    return render(request, "author/login.html", context)


@user_passes_test(is_not_authenticated, login_url='/author/info/')
def register_view(request):
    register_user_form = RegisterUserForm()
    register_form = RegisterForm()

    if request.method == "POST":
        register_user_form = RegisterUserForm(request.POST or None)
        register_form = RegisterForm(request.POST or None, request.FILES or None)

        if register_user_form.is_valid() and register_form.is_valid():
            new_author = register_user_form.save(commit=True)
            new_author.is_active = False
            password = register_user_form.cleaned_data.get("password")
            new_author.set_password(password)
            new_author.save()
            age = register_form.cleaned_data.get("age")
            bio = register_form.cleaned_data.get("bio")
            photo = register_form.cleaned_data.get("photo")

            author = Author.objects.create(
                username=new_author,
                name=new_author.first_name,
                surname=new_author.last_name,
                email=new_author.email,
                earning=0,
                age=age,
                bio=bio,
                photo=photo,
                activation_code=CodeGenerator.create_activation_link_code(size=4, model_=Author)
            )

            # sending mail

            message = f"Aktivasiya kodunuz: \n {author.activation_code}"

            send_mail(
                'Aktivasiya kodu',  # subject
                message,  # message
                'settings.EMAIL_HOST_USER',  # from mail
                [author.email],  # to mail
                fail_silently=False,
            )

            return redirect(reverse_lazy("author:activate", kwargs={"slug": author.slug}))

        else:
            print(register_user_form.errors)

    context = {
        'registerUserForm': register_user_form,
        'registerForm': register_form
    }

    return render(request, "author/register.html", context)


@user_passes_test(is_not_authenticated, login_url='/author/info/')
def activate_account_code_view(request, slug):
    author = get_object_or_404(Author, slug=slug)
    activate_account_form = ActivateAccountForm()

    if request.method == "POST":
        activate_account_form = ActivateAccountForm(request.POST or None)

        if activate_account_form.is_valid():
            if activate_account_form.cleaned_data.get('activation_code') == author.activation_code:
                author.username.is_active = True
                author.username.save()
                author.activation_code = None
                author.save()

                # login(request, user.username)

                return redirect("/author/login/")
            else:
                messages.error(request, 'Şifrə səhvdir')
        else:
            print(activate_account_form.errors)

    context = {
        'code_active': activate_account_form
    }

    return render(request, "author/activate.html", context)


@login_required(login_url="/author/login/")
def logout_view(request):
    try:
        user = get_object_or_404(Author, username=request.user)
        logout(request)
        return redirect("/")

    except Http404:
        return redirect('/author/login/')


@login_required(login_url="/author/login/")
def password_change_view(request):
    try:
        user = get_object_or_404(Author, username=request.user)

        form = PasswordChangeForm(user=request.user)

        if request.method == "POST":
            form = PasswordChangeForm(request.user, data=request.POST)

            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)

                return redirect("/author/login/")

        context = {
            "changePassForm": form
        }

        return render(request, "author/change_password.html", context)

    except Http404:
        return redirect('/author/login/')


@user_passes_test(is_not_authenticated, login_url='/author/info/')
def reset_password_view(request):
    form = ResetPasswordForm()

    if request.method == "POST":
        form = ResetPasswordForm(request.POST or None)

        if form.is_valid():
            email = form.cleaned_data.get("email")

            author = Author.objects.get(username=Users.objects.get(email=email))

            # send mail

            link = request.build_absolute_uri(reverse_lazy("author:reset-complete", kwargs={"slug": author.slug}))
            message = f"Şifrə yeniləmə linkiniz: \n {link}"

            send_mail(
                'Şifrə yeniləmə',  # subject
                message,  # message
                'settings.EMAIL_HOST_USER',  # from mail
                [author.email],  # to mail
                fail_silently=False,
            )

            return redirect("/author/login/")

    context = {
        "resetPassForm": form
    }

    return render(request, "author/reset.html", context)


@user_passes_test(is_not_authenticated, login_url='/author/info/')
def reset_password_complete_view(request, slug):
    author = get_object_or_404(Author, slug=slug)
    form = ResetPasswordCompleteForm(instance=author)

    if request.method == "POST":
        form = ResetPasswordCompleteForm(instance=author.username, data=request.POST)

        if form.is_valid():
            form.save()

            return redirect("/author/login/")

    context = {
        "resetPassCompleteForm": form
    }

    return render(request, "author/reset_complete.html", context)


@login_required(login_url="/author/login/")
def info_view(request):
    try:
        user = get_object_or_404(Author, username=request.user)

        updateUserForm = UpdateUserForm(instance=request.user)
        regForm = RegisterForm(instance=Author.objects.get(username=request.user))

        photo_url = "" if not Author.objects.filter(username=request.user).first().photo else Author.objects.filter(username=request.user).first().photo.url
        warning = ""

        try:
            if request.method == "POST":
                updateUserForm = UpdateUserForm(request.POST or None, instance=request.user)
                regForm = RegisterForm(request.POST or None, request.FILES or None, instance=Author.objects.get(username=request.user))

                if updateUserForm.is_valid():
                    update_author = updateUserForm.save(commit=False)
                    update_author.save()

                    regForm.save()

                    age = regForm.cleaned_data.get("age")
                    bio = regForm.cleaned_data.get("bio")

                    find_author = Users.objects.get(username=user)

                    Author.objects.filter(username=find_author).update(
                        name=update_author.first_name,
                        surname=update_author.last_name,
                        email=update_author.email,
                        age=age,
                        bio=bio
                    )

                    return redirect("/author/info/")

        except ValueError:
            warning = "Xəta! Yenidən cəhd edin!"


        context = {
            'updateUserForm': updateUserForm,
            'updateRegForm': regForm,
            'photo_url': photo_url,
            'warning': warning
        }

        return render(request, "author/info.html", context)

    except Http404:
        return redirect('/author/login/')


@login_required(login_url="/author/login/")
def book_list_view(request):
    try:
        user = get_object_or_404(Author, username=request.user)

        author = Author.objects.get(username=request.user)

        book_list = Book.objects.filter(userauthor=author).annotate(
            author_none=Coalesce(F("author"), Value("Qeyd olunmayıb"))
        )

        paginator = Paginator(book_list, 6)
        page = request.GET.get("page", 1)
        book_list = paginator.get_page(
            page)

        context = {
            "book_list": book_list
        }

        return render(request, "author/book_list.html", context)

    except Http404:
        return redirect('/author/login/')


@login_required(login_url="/author/login/")
def book_create_view(request):
    try:
        user = get_object_or_404(Author, username=request.user)

        bookCreateForm = BookCreateForm()
        bookImageCreateForm = BookImageCreateForm()

        if request.method == "POST":
            bookCreateForm = BookCreateForm(request.POST or None, request=request)
            bookImageCreateForm = BookImageCreateForm(request.POST or None, request.FILES or None)

            if bookCreateForm.is_valid() and bookImageCreateForm.is_valid():
                if not Book.objects.filter(Q(name=bookCreateForm.cleaned_data.get('name'))&Q(userauthor=user)).exists():
                    # To prevent the author from sharing a book with the name he shared before
                    author = bookCreateForm.cleaned_data.get("author")
                    release_date = bookCreateForm.cleaned_data.get("release_date")

                    rentM = request.POST.getlist('rent-month', None)

                    book = Book.objects.create(
                        userauthor=user,
                        name=bookCreateForm.cleaned_data.get("name"),
                        summary=bookCreateForm.cleaned_data.get("summary"),
                        author=author if author != "" else None,
                        category=bookCreateForm.cleaned_data.get("category"),
                        release_date=release_date if release_date != "" else None,
                        rent=bookCreateForm.cleaned_data.get("rent"),
                        quantity=bookCreateForm.cleaned_data.get("quantity"),
                        warehouse=bookCreateForm.cleaned_data.get("warehouse"),
                        status=bookCreateForm.cleaned_data.get("status"),
                        view_count=1,
                        wishlist_count=1
                    )

                    book.set_list_field(rentM)
                    book.save()

                    BookImage.objects.create(
                        book=book,
                        image=bookImageCreateForm.cleaned_data.get("image")
                    )

                    return redirect("/author/book-list/")
                else:
                    messages.error(request, 'Bu adda kitabı öncədən paylaşdınız')

            else:
                print(bookCreateForm.errors, "---", bookImageCreateForm.errors)

        context = {
            'bookCreate': bookCreateForm,
            'bookImageCreateForm': bookImageCreateForm
        }

        return render(request, "author/book_create.html", context)

    except Http404:
        return redirect('/author/login/')


@login_required(login_url="/author/login/")
def book_update_view(request, id):
    try:
        user = get_object_or_404(Author, username=request.user)

        book = get_object_or_404(Book, id=id, userauthor=user)
        bookCopy = book.name
        warehouseCopy = book.warehouse
        BookForm = BookCreateForm(instance=book)

        image = get_object_or_404(BookImage, book=book)
        BookImageForm = BookImageCreateForm(instance=image)

        if request.method == "POST":
            BookForm = BookCreateForm(request.POST or None, instance=book)
            BookImageForm = BookImageCreateForm(request.POST or None, request.FILES or None, instance=image)

            if BookForm.is_valid() and BookImageForm.is_valid():
                author_book_list = Book.objects.filter(Q(userauthor=user)).values_list('name', flat=True)
                # author book list not including updated book

                if warehouseCopy == "Gözlənilir" and BookForm.cleaned_data.get('warehouse') == "Mövcuddur":
                    if book.queue_set.filter(book=book):
                        message = f"Növbə götürdüyünüz '{book.name}' adlı kitab artıq mövcuddur."
                        mail_list = []
                        for get_user_id in book.queue_set.all().values_list('user', flat=True):
                            mail_list.append(f'{User.objects.get(id=get_user_id).email}')

                        send_mail(
                            'Növbə götürdüyünüz kitab',  # subject
                            message,  # message
                            'settings.EMAIL_HOST_USER',  # from mail
                            mail_list,  # to mail
                            fail_silently=False,
                        )

                if BookForm.cleaned_data.get('name') not in author_book_list:
                    book.r_month=book.r_month
                    BookForm.save()
                    BookImageForm.save()

                    return redirect("author:book-update", book.id)
                elif BookForm.cleaned_data.get('name') == bookCopy:
                    book.r_month = book.r_month
                    BookForm.save()
                    BookImageForm.save()

                    return redirect("author:book-update", book.id)
                else:
                    messages.error(request, 'Bu adda kitabınız mövcuddur')
            else:
                print(BookImageForm.errors, "---", BookForm.errors)

        context = {
            "BookForm": BookForm,
            "BookImageForm": BookImageForm,
            "BookPhoto": image,
            'book': book
        }

        return render(request, "author/book_update.html", context)

    except Http404:
        return redirect('/author/login/')


@login_required(login_url="/author/login/")
def book_delete_view(request, id):
    try:
        user = get_object_or_404(Author, username=request.user)
        get_object_or_404(Book, id=id, userauthor=user)

        search = Book.objects.filter(Q(userauthor=user)&Q(id=id))

        if search: search.delete()

        return redirect("author:book-list")
    except Http404:
        return redirect('/author/login/')