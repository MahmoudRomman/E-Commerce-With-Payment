from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [

    path('', views.home, name='home'),
    
    path('products/', views.products, name='products'),
    path('category/<slug:category_slug>/', views.products, name='products_by_category'),

    path('product_detail/<slug:slug>/', views.product_detail, name='product_detail'),

    
    # path('load_products/', views.load_products, name='load_products'),

] 