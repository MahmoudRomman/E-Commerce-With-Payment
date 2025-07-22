from django import forms
from . import models
from django.core.exceptions import ValidationError


class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

    def __init__(self, *args, **kwargs):
        super(OrderCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})




class OrderPayForm(forms.ModelForm):
    class Meta:
        model = models.OrderPay
        fields = ['pay_phone', 'pay_image']


    def clean_pay_phone(self):
        pay_phone = self.cleaned_data.get('pay_phone')
        if not pay_phone.isdigit():
            raise ValidationError("The phone you entered must be integer and not contain any chars!")

        if len(pay_phone) != 11:
            raise ValidationError("The phone length must be 11 number!")

        valid_prifixes = ["010", "011", "012", "015"]
        if str(pay_phone)[0:3] not in valid_prifixes:
        # if not any(pay_phone.startwith(prifix) for prifix in valid_prifixes):
            raise ValidationError(f"The start of the number must be in {valid_prifixes}")
        
        return pay_phone

    # def __init__(self, *args, **kwargs):
    #     super(OrderCreationForm, self).__init__(*args, **kwargs)
    #     for field in self.fields.values():
    #         field.widget.attrs.update({'class': 'form-control'})
