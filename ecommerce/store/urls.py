from django.urls import path
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import (
    CustomLoginView, 
    register, 
    product_detail, 
    order_list, 
    ProductList,
    filtered_products,
    index,
    reset_filters

)

urlpatterns = [
    path('', views.index, name='index'),
    path('store/', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('login/', CustomLoginView.as_view(), name='login'),  # Bejelentkezési URL
    path('register/', views.register, name='register'),  # Regisztrációs URL
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout', kwargs={'next_page': 'store'}),  # Kijelentkezés és átirányítás
    path('orders/', views.order_list, name='order_list'),  # Rendelések listája
    path('api/products/', ProductList.as_view(), name='product-list'),  # API a termékekhez
    path('search/', views.search, name='search'),
    path('filtered-products/', filtered_products, name='filtered_products'),
    path('reset-filters/', reset_filters, name='reset_filters'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

