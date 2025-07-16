from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
# from . import forms
from . import models

# Create your views here.


def home(request):
    return render(request, 'store/home.html')




def products(request):
    products = models.Product.objects.filter(status=models.Status.AVAILABLE)  #type: ignore

    context = {
        'products' : products,
    }
    return render(request, 'store/products.html', context)


def product_detail(request, slug):
    try:
        product = models.Product.objects.get(slug=slug, status=models.Status.AVAILABLE)  #type: ignore
    except ObjectDoesNotExist:
        messages.error(request, 'Please, Go to you email inbox to activate your email first!')
        return redirect('accounts:login')  # redirect to the url page that you want

    context = {
        'product' : product,
    }
    return render(request, 'store/product_detail.html', context)












# import requests
# from django.core.files.base import ContentFile
# from django.http import HttpResponse
# from . import models
# import os

# def load_products(request):
#     response = requests.get('https://fakestoreapi.com/products')
#     cnt = 0
#     for item in response.json():
#         cnt += 1

#         # Download image
#         img_response = requests.get(item['image'])
#         if img_response.status_code == 200:
#             file_name = os.path.basename(item['image'])  # Extract filename from URL
#             image_file = ContentFile(img_response.content, name=file_name)

#             # Create product
#             product = models.Product.objects.create(
#                 name=item['title'],
#                 category=None,  # Set this properly if needed
#                 image=image_file,  # Upload the image content
#                 price=item['price'],
#                 description=item['description']
#             )
#             print("Loaded item no.", cnt)
#         else:
#             print(f"Failed to download image for item no. {cnt}")

#     return HttpResponse("Products loaded successfully.")
