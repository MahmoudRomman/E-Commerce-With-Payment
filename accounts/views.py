from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from . import forms
from . import models

# Create your views here.


def register(request):
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            country = form.cleaned_data['country']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']

            username = email.split('@')[0]

            user = models.Account.objects.create_user(
                first_name = first_name,
                last_name = last_name,
                email = email, username = username,
                country = country, password = password
            )

            user.phone_number = phone_number
            user.save()

            # user activation
            domain_name = get_current_site(request)
            mail_subject = "please activate your account"
            message = render_to_string("link to html page to landing on.", {
                'user' : user,
                'domain' : domain_name,
                'uuid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })

            to_email = email
            send_mail = EmailMessage(mail_subject, message, 
                                    'mahmoud.sayyedahmed900@gmail.com',
                                    to=[to_email])
            send_mail.send()


            return redirect('login' + f"?command=verification&mail={email}")
    else:
        form = forms.RegisterForm()

    context = {
        'form' : form
    }

    return render(request, 'accounts/register.html', context)



    from django.core.mail import send_mail

