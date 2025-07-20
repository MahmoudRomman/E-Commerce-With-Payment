from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [

    path('create/', views.create_order, name='create_order'),
    path('success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
     path('order/<str:order_id>/', views.order_detail, name='order_detail'),

] 