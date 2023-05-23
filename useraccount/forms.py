from django import forms
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
import pathlib

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

        if not user or not User.objects.filter(username__username=username):
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
            self.add_error("username", "Bu adda istifadə hesabı mövcuddur. Fərqli ad daxil edin")
        if email_qs.exists():
            self.add_error("email", "Bu e-poçt adresində istifadəçi hesabı mövcuddur. Fərqli e-poçt daxil edin")
        if not first_name.replace(" ", "").isalpha():
            self.add_error("first_name", "Adınızda yalnız hərflərdən istifadə etməlisiniz.")
        if not last_name.replace(" ", "").isalpha():
            self.add_error("last_name", "Soyadınızda yalnız hərflərdən istifadə etməlisiniz.")
        if len(password) < 6:
            self.add_error("password", "Şifrə ən az 6 dəyər olmalıdır")
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
    age = forms.IntegerField(label="Yaş")
    bio = forms.CharField(min_length=3, max_length=1000, widget=forms.Textarea())

    class Meta:
        model = User
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
            if not User.objects.filter(username=Users.objects.get(email=email)).exists():
                self.add_error("email", "Bu e-poçt adresində istifadəçi hesabı yoxdur")
        else:
            self.add_error("email", "Bu e-poçt adresində istifadəçi hesabı yoxdur")



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


class ActivateAccountForm(forms.ModelForm):
    activation_code = forms.CharField(max_length=20)
    class Meta:
        model = User
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
