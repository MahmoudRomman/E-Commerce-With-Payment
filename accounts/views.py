from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login as auth_login
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
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
            message = render_to_string("accounts/account_verification_email.html", {
                'user' : user,
                'domain' : domain_name,
                'uuid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
            })
            

            to_email = email
            send_mail = EmailMessage(
                mail_subject,
                message,
                'mahmoud.sayyedahmed900@gmail.com',
                to=[to_email]
            )
            send_mail.content_subtype = 'html'
            send_mail.send()

            # return redirect('login')
            # return redirect('accounts:login' + f'?command=verification&mail={email}')


            login_url = reverse('accounts:login')  # generates something like '/accounts/login/'
            return redirect(f"{login_url}?command=verification&mail={email}")





    else:
        form = forms.RegisterForm()

    context = {
        'form' : form
    }

    return render(request, 'accounts/register.html', context)




def login(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            print("Hello")
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            email_exists = models.Account.objects.filter(email=email).exists()
            if email_exists:
                user = authenticate(email=email, password=password)
                if user is None:
                    form.add_error(None, 'Invalid Password.')
                else:
                    if user.is_active:
                        auth_login(request, user)  #type: ignore
                        messages.success(request, 'Login Successfully!')
                        return redirect('store:home')  # redirect to the url page that you want
                    else:
                        messages.error(request, 'Please, Go to you email inbox to activate your email first!')
                        return redirect('accounts:login')  # redirect to the url page that you want
            else:
                form.add_error(None, 'Invalid Email.')
                messages.error(request, 'Please Enter Correct Email!')

    else:
        form = forms.LoginForm()
    
    context = {
        'form' : form
    }
    
    return render(request, 'accounts/login.html', context)



def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = models.Account.objects.get(pk=uid)
    except ObjectDoesNotExist:
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your Account Is Activated!')
        return redirect('accounts:login')
    else:
        messages.success(request, 'Your Account Is Not Activated Yet, Please Check Your Mail And Try Again!')
        return redirect('accounts:register')
    