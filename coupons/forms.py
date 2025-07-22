from django import forms
from . import models



# class ApplyCouponForm(forms.Form):
#     code = forms.CharField()


class ApplyCouponForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'coupon_code',
            'class': 'form-control',
            'placeholder': 'Enter your code'
        })
    )
