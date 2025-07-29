from django.db.models import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

from . import models
from . import forms
from . import tasks
from django.shortcuts import redirect
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
import weasyprint
from django.contrib.admin.views.decorators import staff_member_required
# Create your views here.






@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(models.Order, order_id=order_id)
    html = render_to_string("orders/order_invoice_pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f"filename=order_{order.user.username}_{order.order_id}.pdf"
    weasyprint.HTML(string=html).write_pdf(response)
    return response


def create_order(request):
    cart = request.session.get('cart', {})
    coupon_slug = request.session.get('coupon_slug', {})

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
            if coupon_slug:
                request.session.pop('coupon_slug')
            # after saving order and order items
            tasks.send_order_confirmation_email.delay(order.id) 
            messages.success(request, "Your order placed successfully, You can pay not for it.")
            return redirect('orders:pay_order', order_id=order.order_id) 
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



@login_required
def my_orders(request):
    orders = models.Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


# View for showing the details of a specific order
def order_detail(request, order_id):
    order = get_object_or_404(models.Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def order_pay_by_VF(request, order_id):
    order = get_object_or_404(models.Order, order_id = order_id)
    if request.method == "POST":
        form = forms.OrderPayForm(request.POST, request.FILES)
        if form.is_valid():
            pay_order = form.save(commit=False)
            pay_order.order = order
            order.paid = True
            order.save()
            pay_order.save()
            return redirect("orders:payment_success", order_id=order.order_id)

    else:
        form = forms.OrderPayForm()
    
    context = {
        'order' : order,
        'form' : form,
    }
    return render(request, "orders/pay_form.html", context)



def payment_success(request, order_id):
    order = get_object_or_404(models.Order, order_id=order_id)
    tasks.send_order_pdf.delay(order.id) 
    context = {
        'order' : order,
    }
    return render(request, 'orders/payment_success.html', context)



