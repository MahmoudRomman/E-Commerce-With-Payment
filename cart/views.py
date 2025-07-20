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
from . import forms
from . import models
from store import models as store_models
# Create your views here.



def add_to_cart(request, product_slug, quantity_from_form = 0):
    cart = request.session.get('cart', {})

    product = store_models.Product.objects.get(slug=product_slug)  # type: ignore

    product_key = str(product_slug)
    price = product.price  # This is a Decimal from the model

    if request.method == "POST":
        add_to_cart_form = forms.CartAddProductForm(request.POST)
        if add_to_cart_form.is_valid():
            quantity_from_form = add_to_cart_form.cleaned_data['quantity']
            # Now you can use quantity

            if product_key in cart:
                cart[product_key]['quantity'] += int(quantity_from_form)
                quantity = cart[product_key]['quantity']
                cart[product_key]['total_price'] = str(price * quantity)
                messages.success(request, 'Item quantity updated.')

            else:
                cart[product_key] = {
                    'quantity': int(quantity_from_form),
                    'name': product.name,
                    'price': str(price),  # Convert to string for JSON
                    'total_price': str(price),
                    'image': product.image.url if product.image else '',
                }
                messages.success(request, 'Item added to cart.')
    else:
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
    product_key = str(product_slug)

    try:
        product = store_models.Product.objects.get(slug=product_slug)   #type: ignore
    except ObjectDoesNotExist:
        messages.error(request, 'Product not found.')
        return redirect('cart:view_cart')

    if product_key in cart:
        if cart[product_key]['quantity'] > 1:
            cart[product_key]['quantity'] -= 1
            cart[product_key]['total_price'] = str(product.price * cart[product_key]['quantity'])
            messages.success(request, 'Item quantity updated.')
        else:
            del cart[product_key]
            messages.success(request, 'Item removed from cart.')

        if not cart:
            request.session.pop('cart', None)
        else:
            request.session['cart'] = cart
    else:
        messages.error(request, 'This item is not in your cart.')

    return redirect('cart:view_cart')




def remove_single_item_from_cart(request, product_slug):
    cart = request.session.get('cart', {})
    product_key = str(product_slug)

    if product_key in cart:
        del cart[product_key]
        messages.success(request, 'Item removed from cart.')

        if not cart:
            request.session.pop('cart', None)
        else:
            request.session['cart'] = cart
    else:
        messages.error(request, 'This item is not in your cart.')

    return redirect('cart:view_cart')



def view_cart(request):
    cart = request.session.get('cart', {})
    total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())

    context = {
        'cart': cart,
        'total_cart_price': total_cart_price
    }
    return render(request, 'cart/cart.html', context)



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

#     return render(request, 'cart/cart.html', context)


    