from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('add_to_cart/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug:product_slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/<slug:product_slug>/', views.remove_single_item_from_cart, name='remove_single_item_from_cart'),


    
    path('view_cart/', views.view_cart, name='view_cart'),

] 

