import decimal
from tokenize import Double
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from decimal import Decimal
# from . import forms
from . import models
from store import models as store_models

# Create your views here.


def add_to_cart(request, product_slug):
    cart = request.session.get('cart', {})

    product = store_models.Product.objects.get(slug=product_slug)  # type: ignore

    product_key = str(product_slug)
    price = product.price  # This is a Decimal from the model

    if product_key in cart:
        cart[product_key]['quantity'] += 1
        quantity = cart[product_key]['quantity']
        cart[product_key]['total_price'] = str(price * quantity)
        messages.success(request, 'Item quantity updated.')

    else:
        cart[product_key] = {
            'quantity': 1,
            'name': product.name,
            'price': str(price),  # Convert to string for JSON
            'total_price': str(price),
            'image': product.image.url if product.image else '',
        }
        messages.success(request, 'Item added to cart.')

    request.session['cart'] = cart
    return redirect('cart:view_cart')



def remove_from_cart(request, product_slug):
    cart = request.session.get('cart', {})

    product = store_models.Product.objects.get(slug=product_slug)  # type: ignore

    product_key = str(product_slug)
    price = product.price  # This is a Decimal from the model

    if product_key in cart:
        if cart[product_key]['quantity'] == 1:
            if len(cart) == 0:  # to remove the whole cart session is there is not items 
                del request.session['cart']
                messages.success(request, 'Item removed from cart.')
            else:
                del cart[product_key]
                messages.success(request, 'Item removed from cart.')
        else:
            cart[product_key]['quantity'] -= 1
            quantity = cart[product_key]['quantity']
            cart[product_key]['total_price'] = str(price * quantity)
            messages.success(request, 'Item quantity updated.')
    else:
        messages.error(request, 'This Item is not found in your cart!')
        return redirect('cart:view_cart')

    request.session['cart'] = cart
    return redirect('cart:view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())

    context = {
        'cart': cart,
        'total_cart_price': total_cart_price
    }
    return render(request, 'cart.html', context)



# def view_cart(request):
#     cart = request.session.get('cart', {})

#     for key, val in cart.items():
#         print(key, '-', val)


#     total_quantity = sum(item['quantity'] for item in cart.values())
#     product_name = cart[product_key]['quantity']
#     total_quantity = sum(item['quantity'] for item in cart.values())

#     context = {
#         'cart': cart,
#         'total_quantity': total_quantity,
#     }

#     return render(request, 'cart.html', context)


    