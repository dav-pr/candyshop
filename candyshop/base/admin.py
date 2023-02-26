from django.contrib import admin
from .models import User, Product, Purchase,Return, Cart, CartItem

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Return)
admin.site.register(Cart)
admin.site.register(CartItem)

