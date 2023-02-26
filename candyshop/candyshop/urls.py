"""candyshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import settings
from base.views import SignUpView, MyLoginView, HomePageView, ShopLogoutView, AddProduct, ReturnView, ProductDetail,\
    ProductUpdateView, add_to_cart, CartView, PurchaseListView, buy, CreateReturn, NoticeReturn,  VitalityReturn



urlpatterns = [
    path("admin/", admin.site.urls),
    path('signup.html', SignUpView.as_view(), name='signup'),
    path('signin.html', MyLoginView.as_view(), name='signin'),
    path("logout.html", ShopLogoutView.as_view(), name='logout'),
    path("add_product.html", AddProduct.as_view(), name='add_product'),
    path("returns.html", ReturnView.as_view(), name='returns'),
    path('product_detail/<slug:product_slug>/', ProductDetail.as_view(), name='product_detail'),
    path('product_detail/<slug:product_slug>/edit', ProductUpdateView.as_view(), name='product_edit'),
    path('add_cart/<slug:product_slug>', add_to_cart, name='add_to_cart'),
    path('cart.html', CartView.as_view(), name='cart'),
    path('purchase.html', PurchaseListView.as_view(), name='purchase'),
    path('buy', buy, name='buy'),
    path('return/<int:product_pk>',  CreateReturn.as_view(), name='return'),
    path('notice_return/<int:return_pk>', NoticeReturn.as_view(),name='notice_return' ),
    path('vitality_return/<int:return_pk>', VitalityReturn.as_view(),name='vitality_return' ),
    path("", HomePageView.as_view(), name = 'homepage'),
    path("/",HomePageView.as_view(), name = 'homepage')


]
# параметри нижче стосуються налаштування папки завантаження зображень товарів. Без цих параметрів зображення на
# сторінці не відображаються
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)