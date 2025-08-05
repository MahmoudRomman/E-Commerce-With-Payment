from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from . import forms
from . import models
from store import models as store_models
from coupons.models import Coupon
from coupons.forms import ApplyCouponForm
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





def get_coupon_instance(request):
    coupon_slug = request.session.get('coupon_slug', {})
    if coupon_slug:
        try:
            coupon = Coupon.objects.get(slug=coupon_slug)
            return coupon
        except ObjectDoesNotExist:
            messages.error(request, "the coupon you entered is incorrect or invalid")
    return None




def get_discount_value(request):
    coupon = get_coupon_instance(request)
    if coupon:
        cart = request.session.get('cart', {})
        total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
        res = (coupon.discount / Decimal(100)) * total_cart_price

        return res

    return Decimal(0)



def get_final_cart_cost(request):
    dis_val = get_discount_value(request)
    if dis_val:
        cart = request.session.get('cart', {})
        total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
        final_price = Decimal(total_cart_price - dis_val)
        request.session['get_final_price_after_coupon'] = float(final_price)

    else:
        request.session['get_final_price_after_coupon'] = float(0)





def round_decimal(value):
    if not isinstance(value, Decimal):
        value = Decimal(str(value))  # convert int/float to Decimal safely
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def view_cart(request):
    cart = request.session.get('cart', {})

    form = ApplyCouponForm()
    get_final_cart_cost(request)  # calculate & store in session
    get_final_price_after_coupon = request.session.get('get_final_price_after_coupon', 0)

    if not isinstance(get_final_price_after_coupon, Decimal):
        get_final_price_after_coupon = Decimal(get_final_price_after_coupon)

    total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
    total_cart_price = round_decimal(total_cart_price)
    get_final_price_after_coupon = round_decimal(get_final_price_after_coupon)

    DISCOUNT = False
    if get_final_price_after_coupon == Decimal("0.00"):
        savings = Decimal("0.00")
    else:
        savings = round_decimal(total_cart_price - get_final_price_after_coupon)
        DISCOUNT = True

    context = {
        'cart': cart,
        'total_cart_price': total_cart_price,
        'get_final_price_after_coupon': get_final_price_after_coupon,
        'savings': savings,
        'DISCOUNT': DISCOUNT,
        'form': form,
    }
    return render(request, 'cart/cart.html', context)

