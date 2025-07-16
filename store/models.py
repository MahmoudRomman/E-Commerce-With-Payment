from ast import arg
from random import choices
from django.db import models
from django.utils import timezone
import string
import random

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):

        # Define the characters to choose from
        characters = string.ascii_uppercase + string.digits

        # Generate a random string of 20 characters
        random_string = ''.join(random.choice(characters) for _ in range(20))

        while True:
            new_slug = '-'.join([random_string[i:i+5] for i in range(0, len(random_string), 5)])
            if not Category.objects.filter(slug=new_slug).exists(): #type: ignore
                break
        return new_slug


    def __str__(self):
        return self.name

class Status(models.TextChoices):
    AVAILABLE = "Available"
    DREFT = "Dreft"

class Product(models.Model):
    name = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=False, blank=False)
    image = models.ImageField(upload_to='products')
    description = models.TextField(max_length=1500)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):

        # Define the characters to choose from
        characters = string.ascii_uppercase + string.digits

        # Generate a random string of 20 characters
        random_string = ''.join(random.choice(characters) for _ in range(20))

        while True:
            new_slug = '-'.join([random_string[i:i+5] for i in range(0, len(random_string), 5)])
            if not Category.objects.filter(slug=new_slug).exists(): #type: ignore
                break
        return new_slug


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['created_at'])
        ]



