# Create your models here.

from decimal import Decimal

from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from .constants import START_WALLET_BALANCE


class User(AbstractUser):
    """
    Клас Покупця.  Має такі атрибути:  WALLET_CURRENCY_CHOICES - тип валюти (створено для майбктнього використання)
    wallet_balance - баланс кошелька покупця
    wallet_currency - валюта кошелька.
    """
    WALLET_CURRENCY_CHOICES = (
        ('USD', 'долар США'),
        ('EUR', 'евро'),
        ('GBP', 'британські фунти'),
        ('UAH', 'гривня')
    )
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_currency = models.CharField(max_length=3, choices=WALLET_CURRENCY_CHOICES, default='UAH')


    def __str__(self):
        return self.username

    def save(self, *args, **kwargs) -> None:
        """
        Метод ініціалізує початковий баланс гаманця покупця.
        Можна було вказати в default=START_WALLET_BALANCE, але виришів діяти таким чином.
        :param args:
        :param kwargs:
        :return:
        """
        if not self.id and self.wallet_balance == 0.00:
            self.wallet_balance = START_WALLET_BALANCE
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Product - клас, який визначає модель продукту.
    name  - найменування продукту
    description - опис продукту
    price - ціна продукту за одну одиницю
    image - забраження продукту
    available_quantity- кількість продукту на складі
    slug  - символьне відобьраження назви продукту для URI

    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product/', null=True, blank=True)
    available_quantity = models.PositiveIntegerField(default=0)
    slug = AutoSlugField(populate_from='name', unique=True, db_index=True, verbose_name="URL")


    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Метод повертає абсолютний URL до сторінки з описом продукту
        :return:
        """
        return reverse('product_detail', kwargs={'product_slug': self.slug})


class Purchase(models.Model):
    """
    Purchase - клас, який визначає модель покупки.
    buyer  - покупець,
    product  - придбаний продукт
    quantity - кількість придбаного продукьу
    total_price  - загальна ціна
    purchase_date - час придбання за часом сервера
    purchase_date_user - час придбання за час покупки
    is_active  - ознака того, чи вирішувалось щодо цієї покупки питання про його поверння. Початкове значення False.
    Коли значення цього атрібуту False, то попуч з цим товаром у розділі "Попередні покупки" відображається кнопка
    "Повернути", у протележному випадку не відображається.
    """
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    purchase_date_user = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        ordering = ['purchase_date']

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name}"

    def save(self, *args, **kwargs)->None:
        """
        Метод зменьшує кількість товарів на складі, та зменьшує баланс кошелька покупця
        :param args:
        :param kwargs:
        :return:
        """
        self.total_price = Decimal(self.quantity) * self.product.price
        self.product.available_quantity -= self.quantity
        self.product.save()
        super(Purchase, self).save(*args, **kwargs)


class Return(models.Model):
    """
    Клас Return - визначає модель "Повернення"
    buyer - покупець, який ініціалізував поверення
    purchase - покупка, якої стосується поверення
    return_price  - ціна повернення (для майбутнього використання )
    return_date  -  дата повернення
    is_notice  - ознака чи підтверджено повернення адміністратором. За замовчення False.

    """
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    return_price = models.DecimalField(max_digits=10, decimal_places=2)
    return_date = models.DateTimeField(auto_now_add=True)
    is_notice = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Повернення"
        verbose_name_plural = "Повернення"
        ordering = ['return_date']

    def __str__(self):
        return f"{self.buyer.username} - {self.purchase.product.name}"

    def save(self, *args, **kwargs):
        """
        Метод реалізує логіку повернення  товару вартості товару у гаманець покупця та відповідної кількості
        товару на склад.
        :param args:
        :param kwargs:
        :return:
        """
        if self.is_notice:
            self.return_price = Decimal(self.purchase.quantity) * self.purchase.product.price
            self.purchase.product.available_quantity += self.purchase.quantity
            self.purchase.buyer.wallet_balance += self.return_price
            self.purchase.buyer.save()
            self.purchase.product.save()
        else:
            self.return_price = 0

        super(Return, self).save(*args, **kwargs)


class Cart(models.Model):
    """
    Клас Cart - реалізує модель "Кошик" покупця
    customer - покупець
    created_at - час створення кошику
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"
        ordering = ['created_at']

    def __str__(self):
        return f'Кошик {self.id}'

    @staticmethod
    def total_price(user):
        """
        Метод обраховує загальну вартість кошика
        :param user:
        :return:
        """
        cart_items = CartItem.objects.filter(cart__customer=user)
        return sum(item.total_price() for item in cart_items)


class CartItem(models.Model):
    """
    Клас CartItem - реалізує модель "Елемент кошика"
    cart   - кошик покупця
    product  - продукт, якиц відповідає елементу кошика
    quantity  - кількість продукту, який бажає придбати покупець
    created_at  - час створення елементу кошика
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Елемент кошику"
        verbose_name_plural = "Елементи кошику"
        ordering = ['created_at']

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def total_price(self):
        """
        Метод обраховує вартість відповідної позиції кошика
        :return:
        """
        return self.quantity * self.product.price
