from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from .models import Account

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Account.objects.get(email=email)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Account.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None
