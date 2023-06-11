from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import ContactForm
from django.db.models import Case, When, CharField, F, Q, Sum, Value
from django.db.models.functions import Coalesce, Cast
from django.core.paginator import Paginator
from django.http import JsonResponse
from authoraccount.models import Author
from useraccount.models import User
from django.db.models import Avg, Max
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

def handler404(request, exception):
    return render(request, '404.html', status=404)


def index_view(request):
    homebook = None
    featuredBooks = None
    bestSellingBook = None

    if Book.objects.all():
        homebook = Book.objects.filter(~Q(warehouse="Bitdi")&~Q(status="Deaktiv")).annotate(
            author_none=Coalesce(F("author"), Value("Qeyd olunmayıb"))
        ).order_by('-view_count')[0]

        featuredBooks = Book.objects.filter(~Q(warehouse="Bitdi")&~Q(status="Deaktiv")).annotate(
            author_none=Coalesce(F("author"), Value("Qeyd olunmayıb"))
        ).order_by('-view_count')[:4]

        bestSellingBook = Book.objects.filter(~Q(warehouse="Bitdi")&~Q(status="Deaktiv")).annotate(
            author_none=Coalesce(F("author"), Value("Qeyd olunmayıb"))
        ).order_by('-view_count')[0]

    context = {
        "homebook": homebook,
        "featuredBooks": featuredBooks,
        "bestSellingBook": bestSellingBook
    }

    return render(request, "books/index.html", context)


def about_view(request):
    return render(request, "books/about.html", {})


def shop_view(request):
    books = Book.objects.filter(~Q(warehouse="Bitdi")&~Q(status="Deaktiv")).annotate(
        author_none=Coalesce(F("author"), Value("Qeyd olunmayıb"))
    )

    filter_, filter_dict = Q(), {}

    # ----------------

    years = Book.objects.filter((~Q(release_date=None)&~Q(warehouse="Bitdi")&~Q(status="Deaktiv"))).values_list('release_date', flat=True).distinct()

    # ----------------

    tenants = Author.objects.all()

    # ----------------

    category = request.GET.getlist("category", None)

    if category != "" and category:
        filter_dict["category"] = "".join(f'category={cat}&' for cat in category)
        filter_.add(Q(category__in=category), Q.AND)

    # ----------------

    tenant = request.GET.get("tenant", None)

    if tenant != "" and tenant:
        filter_dict["userauthor"] = tenant
        filter_.add(Q(userauthor=tenant), Q.AND)

   # ----------------

    year = request.GET.get("year", None)

    if year:
        filter_dict["release_date"] = year
        filter_.add(Q(release_date=year), Q.AND)

    # ----------------

    if request.method == "POST":
        search = request.POST.get("search")

        filter_.add(Q(name__icontains=search), Q.AND)


    books = books.filter(filter_)

    paginator = Paginator(books, 6)
    page = request.GET.get("page", 1)
    book_list = paginator.get_page(
        page)

    context = {
        "books": book_list,
        "categories": Category.objects.filter(parent__isnull=True),
        "years": years,
        "tenants": tenants,
        "pagiantor": paginator,
        "filter_dict": filter_dict.values()
    }

    return render(request, "books/shop.html", context)


def cart_view(request):
    context = {}
    return render(request, "books/cart.html", context)


def detail_view(request, id):
    books = get_object_or_404(Book.objects.filter(~Q(warehouse='Bitdi')&~Q(status='Deaktiv')).annotate(
        author_none=Coalesce(F("author"), Value("Qeyd olunmayıb"))
    ).annotate(
        release_date_none=Coalesce(F("release_date"), Value("Qeyd olunmayıb"), output_field=CharField())
    ).annotate(
        category_none=Coalesce(F("category"), Value("Qeyd olunmayıb"), output_field=CharField())
    ), id=id)

    books.view_count += 1
    books.save()


    # -------

    get_user = None

    if request.user.username:
        get_user = User.objects.get(username=request.user) if User.objects.filter(username=request.user).exists() else None

    if request.method == "POST" and "comment" in request.POST:
        comment = request.POST.get("comment")

        if not Comment.objects.filter(user=get_user).exists():
            Comment.objects.create(
                user=get_user,
                book=books,
                author=books.userauthor,
                comment=comment
            )

        return redirect(f"/detail/{books.id}")


    # -------

    month_prices = {}

    for month in books.get_list_field():
        month_prices[month] = int(month) * books.rent

    # -------

    user_qs = User.objects.filter(username=request.user).exists() if request.user.username else False

    check_user_cart = False
    check_user_queue = False

    if user_qs:
        get_user_c = User.objects.get(username=request.user)

        check_user_cart = get_user_c.cart_set.filter(Q(user=get_user_c)&Q(book=books)).exists()
        check_user_queue = get_user_c.queue_set.filter(Q(user=get_user_c)&Q(book=books)).exists()

    # ------

    comments = Comment.objects.filter(book=books.id) if Comment.objects.filter(book=books.id).exists() else None

    context = {
        "bookDetail": books,
        "get_user": get_user,
        "month_prices": month_prices,
        "check_user_cart": check_user_cart,
        "check_user_queue": check_user_queue,
        "comments": comments
    }

    return render(request, "books/detail.html", context)


@login_required(login_url="/user/login/")
def delcomment_view(request):
    data = {}
    get_object_or_404(User, username=request.user)

    comment = get_object_or_404(Comment, id=int(request.POST.get("id")))

    user_comment_vals = User.objects.get(username=request.user).comment_set.all()
    user_values = user_comment_vals.values_list("user", flat=True)
    # get user values from user's comment model

    get_user = User.objects.get(username=request.user)

    if all(user_id == get_user.id for user_id in user_values):
        # Checking that the person who deleted the comment is their own comment
        comment.delete()
        data["success"] = True
    else:
        data["permission"] = False

    return JsonResponse(data)


def wish_view(request):
    data = {}
    book = get_object_or_404(Book, id=int(request.POST.get("id")))

    user_qs = User.objects.filter(username=request.user).exists() if request.user.username else False

    if user_qs:
        get_user = User.objects.get(username=request.user)
        if get_user in book.wishlist.all():
            data["success"] = False
            book.wishlist.remove(get_user)
        else:
            book.wishlist_count += 1
            book.save()
            book.wishlist.add(get_user)
            data["success"] = True
    else:
        data["permission"] = False

    return JsonResponse(data)


def queue_view(request):
    data = {}
    book = get_object_or_404(Book, id=int(request.POST.get("id")))

    user_qs = User.objects.filter(username=request.user).exists() if request.user.username else False

    if user_qs:
        get_user = User.objects.get(username=request.user)
        if get_user.queue_set.filter(Q(user=get_user)&Q(book=book)):
            data["success"] = False
        else:
            Queue.objects.create(
                user=get_user,
                book=book
            )
            data["success"] = True
    else:
        data["permission"] = False

    return JsonResponse(data)


def book_cart_create_view(request):
    data = {}
    book = get_object_or_404(Book, id=int(request.POST.get("id")))

    user_qs = User.objects.filter(username=request.user).exists() if request.user.username else False

    check_user_cart = False

    if user_qs:
        get_user_c = User.objects.get(username=request.user)
        check_user_cart = get_user_c.cart_set.filter(Q(user=get_user_c) & Q(book=book)).exists()

        if request.method == "POST" and "month" in request.POST:
            user_qs_c = User.objects.filter(username=request.user).exists()

            if user_qs_c:
                get_user_c = User.objects.get(username=request.user)

                if not check_user_cart:
                    Cart.objects.get_or_create(
                        user=get_user_c,
                        book=book,
                        month=request.POST.get('month'),
                        author=book.userauthor
                    )

                    data["success"] = True

        data["check_user_cart"] = check_user_cart

    else:
        data["permission"] = False

    return JsonResponse(data)


def contact_view(request):
    contactForm = ContactForm()

    if request.method == "POST":
        contactForm = ContactForm(request.POST or None)

        if contactForm.is_valid():
            contactForm.save()

            # sending mail

            send_mail(
                'Booksaw Contact',  # subject
                contactForm.cleaned_data.get('message'),  # message
                'settings.EMAIL_HOST_USER',  # from mail
                ['youremail@gmail.com', ],  # to mail
                fail_silently=False,
            )

            return redirect("books:contact")


    context = {
        "contact": contactForm
    }

    return render(request, "books/contact.html", context)


def base_view(request):
    data = {}

    user_qs = Users.objects.filter(username=request.user).exists() if request.user.username else False

    if user_qs:
        get_user = Users.objects.get(username=request.user)
        if Author.objects.filter(username=Users.objects.get(username=get_user)).exists():
            data["account"] = "Author"
        elif User.objects.filter(username=Users.objects.get(username=get_user)).exists():
            data = {
                "account": "User",
                "cart_count": User.objects.get(username=request.user).cart_set.count()
            }
    else:
        data["account"] = "Anonym"

    return JsonResponse(data)
