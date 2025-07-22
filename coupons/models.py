from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import string
import random
# Create your models here.


class Coupon(models.Model):
    code = models.CharField(max_length=50, null=False, blank=False, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="The discount percentage from 0 to 100%")
    active = models.BooleanField(default=False)
    slug = models.SlugField(blank=True)


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
            if not Coupon.objects.filter(slug=new_slug).exists(): #type: ignore
                break
        return new_slug



    def __str__(self):
        return self.code









