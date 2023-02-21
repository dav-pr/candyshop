from django.contrib.auth import login, authenticate, get_user_model
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from .forms import CustomUserCreationForm, LoginForm, AddProductForm
from .models import Product, Return





@method_decorator(user_passes_test(lambda u: not u.is_authenticated, login_url='homepage'), name='dispatch')
class SignUpView(CreateView):

    form_class = CustomUserCreationForm
    success_url = reverse_lazy('homepage')
    template_name = 'base/signup.html'




@method_decorator(user_passes_test(lambda u: not u.is_authenticated, login_url='homepage'), name='dispatch')
class MyLoginView(LoginView):
    template_name = 'base/signin.html'  # шлях до вашого шаблону
    success_url = reverse_lazy('homepage')  # URL для перенаправлення після успішної авторизації
    authentication_form = LoginForm


class ShopLogoutView(LogoutView):
    next_page = reverse_lazy('homepage')


class MenuMixin(View):
    def get_menu_admin(self):
        menu = [
            {'url_name': 'homepage', 'title': 'Перегляд товарів'},
            {'url_name': 'add_product', 'title': 'Додавання товарів'},
            {'url_name': 'homepage', 'title': 'Зміна товарів'},
            {'url_name': 'returns', 'title': 'Перегляд повернень'},
            #{'url': reverse('about'), 'label': 'Про нас'},
            #{'url': reverse('contact'), 'label': 'Контакти'},
        ]
        return menu

    def get_menu_user(self):
        menu = [
            {'url_name': 'homepage', 'title': 'Перегляд товарів'},
            {'url_name': 'homepage', 'title': 'Попередні покупки'},
            {'url_name': 'homepage', 'title': 'Кошик'}
        ]
        return menu


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_superuser:
            context['menu'] = self.get_menu_admin()
        else:
            if self.request.user.is_authenticated:
                context['menu'] = self.get_menu_user()

        return context


class HomePageView(MenuMixin, ListView):
    model = Product
    template_name = 'base/homepage.html'
    context_object_name = 'products'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Product.objects.all():
            context['title_product'] = "Наші товари"
        else:
            context['title_product'] = "Товари відсутні"

        return context

@method_decorator(user_passes_test(lambda u:  u.is_superuser, login_url='homepage'), name='dispatch')
class ReturnView(MenuMixin, ListView):
    model = Return
    template_name = 'base/returns.html'
    context_object_name = 'returns'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Return.objects.all():
            context['title_returns'] = "Повернення"
        else:
            context['title_returns'] = "Повернення відсутні"

        return context


@method_decorator(user_passes_test(lambda u: u.is_superuser, login_url='homepage'), name='dispatch')
class AddProduct(CreateView):
    form_class = AddProductForm
    template_name = 'base/add_product.html'
    success_url = reverse_lazy('add_product')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'base/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['title'] = context['post']
        # context['menu'] = menu
        return context

#class ProductView(ListView):
#    model = Product
#    template_name = ''