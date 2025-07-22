from django.shortcuts import redirect, render
from . import forms, models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


def apply_coupon(request):
    if request.method == "POST":
        now = timezone.now()
        form = forms.ApplyCouponForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            try:
                coupon = models.Coupon.objects.get(
                    code__iexact=code,
                    valid_from__lte=now,
                    valid_to__gte=now,
                    active=True
                )
                request.session['coupon_slug'] = coupon.slug
            except ObjectDoesNotExist:
                request.session['coupon_slug'] = None
    return redirect('cart:view_cart')
