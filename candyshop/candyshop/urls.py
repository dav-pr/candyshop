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
from base.views import SignUpView, MyLoginView, HomePageView, ShopLogoutView, AddProduct, ReturnView, ProductDetail



urlpatterns = [
    path("admin/", admin.site.urls),
    path('signup.html', SignUpView.as_view(), name='signup'),
    path('signin.html', MyLoginView.as_view(), name='signin'),
    path("logout.html", ShopLogoutView.as_view(), name='logout'),
    path("add_product.html", AddProduct.as_view(), name='add_product'),
    path("returns.html", ReturnView.as_view(), name='returns'),
    path('product_detail/<slug:product_slug>/', ProductDetail.as_view(), name='product_detail'),

    path("", HomePageView.as_view(), name = 'homepage'),
    path("/",HomePageView.as_view(), name = 'homepage')

    # path("signin.html", sign_in, name = 'signin'),
    # path("signup.html", sign_up, name = 'signup'),
    # path("logout.html", logout_view, name = 'logout'),

]
