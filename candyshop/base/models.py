from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from autoslug import AutoSlugField
from django.urls import reverse

class User(AbstractUser):
    WALLET_CURRENCY_CHOICES = (
        ('USD', 'долар США'),
        ('EUR', 'евро'),
        ('GBP', 'британські фунти'),
        ('UAH', 'гривня')
    )
    is_buyer = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_currency = models.CharField(max_length=3, choices=WALLET_CURRENCY_CHOICES, default='USD')



    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.id and self.wallet_balance == 0.00:
            self.wallet_balance = 100.00
        super().save(*args, **kwargs)

    # def clean(self):
    #     super().clean()
    #     email = self.email
    #     users_with_email = User.objects.filter(email=email)
    #     if self.pk:
    #         users_with_email = users_with_email.exclude(pk=self.pk)
    #     if users_with_email.exists():
    #         raise ValidationError(
    #             _('A user with this email already exists.'),
    #             code='duplicate_email',
    #         )



class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product', null=True, blank=True)
    available_quantity = models.PositiveIntegerField(default=0)
    slug = AutoSlugField(populate_from='name', unique=True, db_index=True, verbose_name="URL" )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})


class Purchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"
        ordering = ['purchase_date']

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name}"

    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.quantity) * self.product.price
        self.product.available_quantity -= self.quantity
        self.product.save()
        super(Purchase, self).save(*args, **kwargs)

class Return(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    return_price = models.DecimalField(max_digits=10, decimal_places=2)
    return_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Повернення"
        verbose_name_plural = "Повернення"
        ordering = ['return_date']

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name}"

    def save(self, *args, **kwargs):
        self.return_price = Decimal(self.quantity) * self.product.price
        self.product.available_quantity += self.quantity
        self.product.save()
        super(Return, self).save(*args, **kwargs)


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"
        ordering = ['created_at']

    def __str__(self):
        return f'Кошик {self.id}'

class CartItem(models.Model):
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
        return self.quantity * self.product.price
