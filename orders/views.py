from django.db.models import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

from . import models
from . import forms
from django.shortcuts import redirect
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
# Create your views here.



def send_order_confirmation_email(order):
    subject = f"Order Confirmation - {order.order_id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email

    html_content = render_to_string('orders/email_order_confirmation.html', {'order': order})
    text_content = f"Thank you for your order {order.order_id}. Please view the full email in HTML."

    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()




def create_order(request):
    cart = request.session.get('cart', {})
    success = False

    if request.method == "POST":
        form = forms.OrderCreationForm(request.POST)
        if form.is_valid():
            if not cart:  # prevent creating order without items
                messages.error(request, "Your cart is empty.")
                return redirect('cart:view_cart')

            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for key, val in cart.items():
                try:
                    product = models.Product.objects.get(slug=key)  # type: ignore
                except ObjectDoesNotExist:
                    messages.error(request, "One or more products no longer exist.")
                    return redirect('cart:view_cart')

                models.OrderItem.objects.create(  # type: ignore
                    order=order,
                    product=product,
                    quantity=val['quantity'],
                    price=val['total_price']
                )
            # Clear cart after successful order
            request.session.pop('cart')
            # after saving order and order items
            send_order_confirmation_email(order)
            messages.success(request, "Order placed successfully!")
            return redirect('orders:order_success')  # ← recommended: show success page
    else:
        form = forms.OrderCreationForm()

    total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
    context = {
        'form': form,
        'cart': cart,
        'total_cart_price': total_cart_price,
        'success': success,
    }
    return render(request, 'orders/create_order.html', context)





def order_success(request):
    return render(request, 'orders/order_success.html')





@login_required
def my_orders(request):
    orders = models.Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


# View for showing the details of a specific order
def order_detail(request, order_id):
    order = get_object_or_404(models.Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
