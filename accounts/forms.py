from dataclasses import fields
from django import  forms
from django.forms import widgets
from . import models


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = models.Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'country']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Your passwords don't match!")

        return cleaned_data  


