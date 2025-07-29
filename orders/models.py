from argparse import Namespace
from unicodedata import digit
from typing_extensions import ReadOnly
from django.db import models
from store.models import Product
import string
import random
from accounts.models import Account
# Create your models here.



class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.CharField(max_length=10, unique=True)
    first_name = models.CharField(max_length=250, null=False, blank=False)
    last_name = models.CharField(max_length=250, null=False, blank=False)
    email = models.EmailField()
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    postal_code = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)   #type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'])
        ]



    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_unique_order_id()
        super().save(*args, **kwargs)

    def generate_unique_order_id(self):

        # Define the characters to choose from
        characters = string.ascii_uppercase + string.digits

        # Generate a random string of 20 characters
        random_string = ''.join(random.choice(characters) for _ in range(20))

        while True:
            new_order_id = '-'.join([random_string[i:i+5] for i in range(0, len(random_string), 5)])
            if not Order.objects.filter(order_id=new_order_id).exists(): #type: ignore
                break
        return new_order_id

    def __str__(self):
        return f"Order ID: {self.order_id}"


    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())  #type: ignore






class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)   #type: ignore


    def __str__(self):
        return str(self.id) #type: ignore

    def get_cost(self):
        return self.quantity * self.price   #type: ignore





        


class OrderPay(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pay_phone = models.CharField(max_length=11)
    pay_image = models.ImageField(upload_to='orders/payments')
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.order.order_id) #type: ignore

    class Meta:
        ordering = ['-created']





        