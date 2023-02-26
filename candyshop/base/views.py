import pytz
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, LoginForm, AddProductForm
from .models import Product, Return, CartItem, Cart, Purchase
from .constants import *


@method_decorator(user_passes_test(lambda u: not u.is_authenticated, login_url='homepage'), name='dispatch')
class SignUpView(CreateView):
    """
    View реєстрації користувача
    """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('homepage')
    template_name = 'base/signup.html'


@method_decorator(user_passes_test(lambda u: not u.is_authenticated, login_url='homepage'), name='dispatch')
class MyLoginView(LoginView):
    """
    View авторизації користувача
    """
    template_name = 'base/signin.html'  # шлях до вашого шаблону
    success_url = reverse_lazy('homepage')  # URL для перенаправлення після успішної авторизації
    authentication_form = LoginForm


class ShopLogoutView(LogoutView):
    """View логаута користувача"""
    next_page = reverse_lazy('homepage')


class MenuMixin(View):
    """
    View - меню користувача та адміністратора. Наслідується іншими класами.
    """
    @staticmethod
    def get_menu_admin():
        menu = [
            {'url_name': 'add_product', 'title': 'Додавання товарів'},
            {'url_name': 'returns', 'title': 'Перегляд повернень'},
        ]
        return menu

    @staticmethod
    def get_menu_user():
        menu = [
            {'url_name': 'purchase', 'title': 'Попередні покупки'},
            {'url_name': 'cart', 'title': 'Кошик'}
        ]
        return menu

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_superuser:
            context['menu'] = self.get_menu_admin()
        else:
            if self.request.user.is_authenticated:
                context['menu'] = self.get_menu_user()
                context['wallet_balance'] = self.request.user.wallet_balance
                context['wallet_currency'] = self.request.user.wallet_currency

        return context


class HomePageView(MenuMixin, ListView):
    """
    View - головний сторінки
    """
    model = Product
    template_name = 'base/homepage.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Product.objects.all():
            context['title_product'] = OUR_PRODUCT
        else:
            context['title_product'] = EMPTY_PRODUCT

        return context


@method_decorator(user_passes_test(lambda u: u.is_superuser, login_url='homepage'), name='dispatch')
class ReturnView(MenuMixin, ListView):
    """
    View - сторінки з відображенням запитів на поверення товарів
    """
    model = Return
    template_name = 'base/returns.html'
    context_object_name = 'returns'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Return.objects.all():
            context['title_returns'] = RETURN_TITLE
        else:
            context['title_returns'] = RETURN_TITLE_EMPTY

        return context


@method_decorator(user_passes_test(lambda u: u.is_superuser, login_url='homepage'), name='dispatch')
class AddProduct(MenuMixin, CreateView):
    """
    View - сторінки з додаванням нового товару
    """
    form_class = AddProductForm
    template_name = 'base/add_product.html'
    success_url = reverse_lazy('add_product')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(user_passes_test(lambda u: u.is_superuser, login_url='homepage'), name='dispatch')
class ProductUpdateView(MenuMixin, UpdateView):
    """
    View - сторінки з оновленням інформації про товарі
    """
    model = Product
    fields = ['name', 'description', 'price', 'image', 'available_quantity']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('homepage')
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'


class ProductDetail(MenuMixin, DetailView):
    """
    View - сторінки з детальною інформацією про товар
    """
    model = Product
    template_name = 'base/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'


@login_required
def add_to_cart(request, product_slug):
    """
    Функція реалізуває логіки додавання товару до кошику.
    :param request:
    :param product_slug:
    :return:
    """
    cart, created = Cart.objects.get_or_create(customer=request.user)
    product = get_object_or_404(Product, slug=product_slug)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += int(request.POST['quantity'])
        cart_item.save()
    return redirect('homepage')


class CartView(LoginRequiredMixin, MenuMixin, ListView):
    """
    View сторінки з даними кошика.
    """
    model = CartItem
    template_name = 'base/cart.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = Cart.objects.get(customer=self.request.user)
        total_price = cart.total_price(self.request.user)
        if total_price:
            context['title_cart'] = CART_TITLE
            context['total_price'] = total_price
            context['cart_id'] = cart.id

        else:
            context['title_cart'] = CART_TITLE_EMPTY
            context['total_price'] = 0

        return context

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user)


class PurchaseListView(LoginRequiredMixin, MenuMixin, ListView):
    """
    View сторінки з інформаціє про покупки
    """
    model = Purchase
    template_name = 'base/purchase.html'
    context_object_name = 'purchases'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if Purchase.objects.filter(buyer=self.request.user):
            context['title_purchase'] = PURCHASE_TITLE
        else:
            context['title_purchase'] = PURCHASE_TITLE_EMPTY
        return context


def check_available_quantity(cart):
    """
    Метод перевіряє наявність необхідної кількості товару на складі
    :param cart: кошик покупця
    :return: повертає True коли товарів достатньо
    """
    cart_items = CartItem.objects.filter(cart=cart)
    for item in cart_items:
        if item.product.available_quantity < item.quantity:
            return item.product.pk
    return True


def process_buy(cart, request):
    """
    Метод реалізує логіки "покупки"
    :param cart:
    :param request:
    :return:
    """
    # отримуємо елеименти кошику
    cart_items = CartItem.objects.filter(cart=cart)
    # цікл проходить по кожному елементу кошика
    for item in cart_items:
        # створюємо екземпляр класу "Покупка"
        purchase_inst = Purchase(buyer=request.user, product=item.product, quantity=item.quantity,
                                 total_price=item.total_price())
        # зменшуємо баланс покупця
        request.user.wallet_balance -= item.total_price()
        # зменшуємо кількість товара на склада
        item.product.available_quantity -= item.quantity

        # Отримуємо часовий пояс користувача
        user_tzname = request.headers.get('HTTP_ACCEPT_TIMEZONE')
        user_timezone = pytz.timezone(user_tzname) if user_tzname else pytz.utc
        # Отримуємо час покупки у форматі UTC
        purchase_time_utc = timezone.now()
        # Конвертуємо час покупки до часового поясу користувача
        purchase_inst.purchase_date_user = purchase_time_utc.astimezone(user_timezone)
        item.product.save()
        request.user.save()
        purchase_inst.save()
        cart_items.delete()


@login_required
def buy(request):
    """
    Метод здійснює перевірки перед реалізаціє логіки "покупки"
    :param request:
    :return:
    """
    if request.POST:
        cart = Cart.objects.get(customer=request.user)
        total_price = cart.total_price(request.user)
        if total_price > request.user.wallet_balance:
            return HttpResponse(NO_MONEY)
        else:
            check = check_available_quantity(cart)
        if isinstance(check, bool) and check:
            process_buy(cart, request)

        else:
            return HttpResponse(f'На складі немає такої кількості {Product.objects.get(pk=check).name}')

        return redirect('homepage')


class CreateReturn(CreateView):
    """
    Клас для створення "Повернення"
    """
    model = Return

    def post(self, request, *args, **kwargs):

        buyer = request.user
        purchase = Purchase.objects.get(pk=request.POST['purchase_pk'])
        duration = (timezone.now() - purchase.purchase_date).total_seconds()
        if duration < DURATION_LIMIT:
            purchase.is_active = False
            obj = Return(buyer=buyer, purchase=purchase, is_notice=False)
            obj.save()
            purchase.save()
            return redirect('purchase')

        else:
            return HttpResponse(NO_RETURN)


class NoticeReturn(UpdateView):
    """
    Реалізація обробки дій користувача  із створення  повернення товару
    """
    model = Return

    def post(self, request, *args, **kwargs):
        return_inst = Return.objects.get(pk=request.POST['return_pk'])
        duration = (timezone.now() - return_inst.purchase.purchase_date).total_seconds()
        if duration < DURATION_LIMIT:
            return_inst.is_notice = True
            return_inst.save()
            return_inst.purchase.delete()
            return redirect('returns')
        else:
            return HttpResponse(NO_RETURN)


class VitalityReturn(NoticeReturn):
    """
    Реалізація дій адміністратора із підтвердження поверненння товару
    """

    def post(self, request, *args, **kwargs):
        return_inst = Return.objects.get(pk=request.POST['return_pk'])
        return_inst.delete()
        return redirect('returns')
