from celery import shared_task
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives, EmailMessage
from io import BytesIO
from xhtml2pdf import pisa
from .models import Order
import weasyprint



@shared_task
def send_order_confirmation_email(order_id):
    from .models import Order  # avoid circular import
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    subject = f"Order Confirmation - {order.order_id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email  # this is a string

    html_content = render_to_string('orders/email_order_confirmation.html', {'order': order})
    text_content = f"Thank you for your order {order.order_id}. Please view the full email in HTML."

    # Correct: wrap to_email in a list
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    email.send()

    return True


@shared_task
def send_order_pdf(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    subject = f"Order Invoice - {order.order_id}"
    message = f"Hi {order.first_name} {order.last_name}, you have successfully placed an order with ID: {order.order_id}."

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]  # already a list, do not wrap again

    html_content = render_to_string('orders/order_invoice_pdf.html', {'order': order})

    out = BytesIO()
    weasyprint.HTML(string=html_content, base_url=settings.BASE_DIR).write_pdf(out)
    out.seek(0)

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=to_email  # correct
    )

    email.attach(f"Order_{order.order_id}.pdf", out.read(), "application/pdf")
    email.send()

    return True
