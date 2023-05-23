from django import forms
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q, F
from books.models import Book, BookImage, warehouse, status, Category
import pathlib
import datetime

class LoginForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, label='Şifrə')

    class Meta:
        model = Users
        fields = ("username", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    "class": "form-control",
            })

        self.fields['username'].widget.attrs.update({"min_length": 3, "max_length": 200})

    def clean(self):
        attrs = self.cleaned_data

        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)

        if not user or not Author.objects.filter(username__username=username):
            self.add_error("username", "İstifadəçi adı və ya şifrə yanlışdır")

        return attrs


class RegisterUserForm(forms.ModelForm):
    password = forms.CharField(min_length=6, max_length=200, widget=forms.PasswordInput, label="Şifrə")
    password_confirm = forms.CharField(min_length=6, max_length=200, widget=forms.PasswordInput, label="Şifrə təstiqi")

    class Meta:
        model = Users
        fields = ("username", "email", "first_name", "last_name", "password", "password_confirm")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    "class": "form-control",
            })

        self.fields['username'].widget.attrs.update({"min_length": 3, "max_length": 200})
        self.fields['email'].widget.attrs.update({"min_length": 5, "max_length": 255})
        self.fields['first_name'].widget.attrs.update({"min_length": 3, "max_length": 200})
        self.fields['last_name'].widget.attrs.update({"min_length": 3, "max_length": 200})


    def clean(self):
        attrs = self.cleaned_data

        username = attrs.get("username")
        email = attrs.get("email")
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        user_qs = Users.objects.filter(username=username)
        email_qs = Users.objects.filter(email=email)

        if user_qs.exists():
            self.add_error("username", "Bu adda kirayəçi hesabı mövcuddur. Fərqli ad daxil edin")
        if email_qs.exists():
            self.add_error("email", "Bu e-poçt adresində kirayəçi hesabı mövcuddur. Fərqli e-poçt daxil edin")
        if not first_name.replace(" ", "").isalpha():
            self.add_error("first_name", "Adınızda yalnız hərflərdən istifadə etməlisiniz")
        if not last_name.replace(" ", "").isalpha():
            self.add_error("last_name", "Soyadınızda yalnız hərflərdən istifadə etməlisiniz")
        if len(password) < 6:
            self.add_error("password", "Şifrə ən az 6 simvol olmalıdır")
        if password != password_confirm:
            self.add_error("password_confirm", "Şifrəniz ilə doğrulama şifrəniz eyni deyil")
        if not password.strip()[0].isalpha():
            self.add_error("password", "Şifrəniz hərif ilə başlamalıdır")
        if password.isalnum():
            self.add_error("password", "Şifrənizdə simvol istifadə etməlisiniz")

        return attrs


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    "class": "form-control",
            })

        self.fields['email'].widget.attrs.update({"min_length": 5, "max_length": 255})
        self.fields['first_name'].widget.attrs.update({"min_length": 3, "max_length": 200})
        self.fields['last_name'].widget.attrs.update({"min_length": 3, "max_length": 200})


    def clean(self):
        attrs = self.cleaned_data

        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")

        if not first_name.replace(" ", "").isalpha():
            self.add_error("first_name", "Adınızda yalnız hərflərdən istifadə etməlisiniz.")
        if not last_name.replace(" ", "").isalpha():
            self.add_error("last_name", "Soyadınızda yalnız hərflərdən istifadə etməlisiniz.")


class RegisterForm(forms.ModelForm):
    age = forms.IntegerField(label="Yaş", required=False)
    bio = forms.CharField(min_length=3, max_length=1000, required=False, widget=forms.Textarea())

    class Meta:
        model = Author
        fields = ("age", "bio", "photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                "class": "form-control",
            })

    def clean(self):
        age = self.cleaned_data.get("age")
        photo = self.cleaned_data.get("photo")

        if photo is not None and photo is not False:
            photo_path = pathlib.Path(str(photo)).suffix
            if photo_path not in ['.jpg', '.jpeg', '.png']:
                self.add_error("photo", "Sadəcə jpg, jpeg və png formatında şəkil yüklənə bilər")

        if age < 18:
            self.add_error("age", "18 yaşdan aşağı kirayəçi qeydiyyatı qadağandır")

        return self.cleaned_data


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                "class": "form-control",
            })


class ResetPasswordForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ("email", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    "class": "form-control",
            })

    def clean(self):
        email = self.cleaned_data.get("email")

        if Users.objects.filter(email=email).exists():
            if not Author.objects.filter(username=Users.objects.get(email=email)).exists():
                self.add_error("email", "Daxil etdiyiniz e-poçt adresində kirayəçi hesabı yoxdur")
        else:
            self.add_error("email", "Bu e-poçt adresində kirayəçi hesabı yoxdur")


class ResetPasswordCompleteForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Yeni şifrə")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Yeni şifrə təstiqləmə")

    class Meta:
        model = Users
        fields = ("password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    "class": "form-control",
            })

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if len(password1.strip()) < 6:
            self.add_error("password1", "Şifrə 6 simvoldan az olmamalıdır")

        if password1 != password2:
            self.add_error("password2", "Şifrələr eyni deyil")

        return self.cleaned_data

    def save(self):
        password1 = self.cleaned_data.get("password1")
        self.instance.set_password(password1)
        self.instance.save()

        return self.instance

class BookCreateForm(forms.ModelForm):
    name = forms.CharField(min_length=2, max_length=300, label="Adı")
    summary = forms.CharField(min_length=5, max_length=2000, label="Məzmunu", widget=forms.Textarea())
    author = forms.CharField(max_length=300, label="Yazar adı", required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(parent__isnull=False), label="Kateqoriyası", required=False)
    release_date = forms.IntegerField(label="Nəşr ili", required=False)
    rent = forms.IntegerField(label="1 aylıq kiralama qiyməti")
    quantity = forms.IntegerField(label="Sayı")
    warehouse = forms.ChoiceField(choices=warehouse, label="Anbar durumu")
    status = forms.ChoiceField(choices=status, label="Status")

    class Meta:
        model = Book
        exclude = ("userauthor", "r_month", "wishlist", "view_count", 'wishlist_count')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                "class": "form-control",
            })

    def clean(self):
        name = self.cleaned_data.get("name")
        author = self.cleaned_data.get("author")
        release_date = self.cleaned_data.get("release_date")
        quantity = self.cleaned_data.get("quantity")
        rent = self.cleaned_data.get("rent")
        warehouse = self.cleaned_data.get("warehouse")
        status = self.cleaned_data.get("status")

        current_year = datetime.datetime.now().year

        if release_date:
            if release_date > current_year:
                self.add_error("release_date", "Kitabın nəşr ili cari ildən artıq olmamalıdır.")
        if int(quantity) < 1 and warehouse == "Mövcuddur":
            self.add_error("warehouse", "Məhsulun anbardada var olma durumunu seçin. Sayı 0 olan məhsul mövcud ola bilməz.")
        if int(rent) < 3 or int(rent) > 500:
            self.add_error("rent", "Məhsulun 3 aylıq qiyməti 3 AZN-dən az və 500 AZN-dən çox olmamalıdır.")
        if author:
            if not author.replace(" ", "").replace(",", "").replace(".", "").isalpha():
                self.add_error("author", "Yazar adında yalnız hərflərdən istifadə edilməlidir.")


class BookImageCreateForm(forms.ModelForm):
    image = forms.ImageField(label="Şəkli")

    class Meta:
        model = BookImage
        fields = ('image',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                "class": "form-control",
            })

    def clean(self):
        image = self.cleaned_data.get("image")

        if image is not None and image is not False:
            photo_path = pathlib.Path(str(image)).suffix
            if photo_path not in ['.jpg', '.jpeg', '.png']:
                self.add_error("image", "Sadəcə jpg, jpeg və png formatında şəkil yüklənə bilər")

        return self.cleaned_data


class ActivateAccountForm(forms.ModelForm):
    activation_code = forms.CharField(max_length=20, label="Şifrə")
    class Meta:
        model = Author
        fields = ('activation_code', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                    "class": "form-control",
            })

    def clean(self):
        activation_code = self.cleaned_data.get("activation_code")

        if activation_code:
            if not activation_code.isalnum():
                self.add_error("activation_code", "Şifrə yanlışdır")