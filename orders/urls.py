from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [

    path('create/', views.create_order, name='create_order'),
    path('pay_order/<str:order_id>/', views.order_pay_by_VF, name='pay_order'),

    
    path('payment_success/<str:order_id>/', views.payment_success, name='payment_success'),
    path('admin/pdf/<str:order_id>/', views.admin_order_pdf, name='admin_order_pdf'),

    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),

] 