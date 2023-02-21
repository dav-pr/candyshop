from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
#from django.contrib.auth.models import User
from .models import Product

from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=31, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


    # def save(self, commit=True):
    #     user = super(CustomUserCreationForm, self).save(commit=False)
    #     user.is_active = False
    #     if commit:
    #         user.save()
    #         uid = urlsafe_base64_encode(force_bytes(user.pk))
    #         token = default_token_generator.make_token(user)
    #         subject = 'Activate your account'
    #         message = f'Activate your account by clicking this link http://127.0.0.1:8000/accounts/activate/{uid}/{token}'
    #         from_email = 'your_email@example.com'
    #         recipient_list = [self.cleaned_data.get('email'), ]
    #         send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    #     return user



class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class AddProductForm(forms.ModelForm):


    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'price', 'available_quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

