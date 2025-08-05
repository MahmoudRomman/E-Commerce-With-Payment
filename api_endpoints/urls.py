from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),

    # store endpoints
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('category/<slug:category_slug>/', views.products, name='products_by_category'),
    path('product_detail/<slug:slug>/', views.product_detail, name='product_detail'),


    # orders endpoints
    path('create/', views.create_order, name='create_order'),
    path('pay_order/<str:order_id>/', views.order_pay_by_VF, name='pay_order'),
    path('payment_success/<str:order_id>/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),


    # cart endpoints
    path('add_to_cart/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug:product_slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<slug:product_slug>/', views.remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),

    # coupon endpoints
    path('apply/', views.apply_coupon, name='apply_coupon'),

]