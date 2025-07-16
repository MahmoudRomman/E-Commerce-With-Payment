from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import pycountry    #type: ignore
# Create your models here.



class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, country, password=None):
        if not email:
            raise ValueError("User must have an email address.")
        if not username:
            raise ValueError("User must have a username.")

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            country=country,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, country='EG', password=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            country=country,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user



def get_countries():
    countries = list(pycountry.countries)
    country_choices = [(country.alpha_2, country.name) for country in countries]    #type: ignore
    return country_choices


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)
    country = models.CharField(max_length=2, choices=get_countries(), default="EG")
    

    is_active = models.BooleanField(default=False)  #type: ignore
    is_staff = models.BooleanField(default=False)  #type: ignore
    is_admin = models.BooleanField(default=False)  #type: ignore
    is_superadmin = models.BooleanField(default=False)  #type: ignore

    join_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'country']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True



