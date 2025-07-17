from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
# from . import forms
from . import models

# Create your views here.


def home(request):

    # del request.session['cart']
    return render(request, 'store/home.html')



def products(request, category_slug=None):
    category = None
    categories = models.Category.objects.all() #type: ignore

    query = request.GET.get('q', '')  # Get query string from ?q=...
    products = models.Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query),    #type: ignore
                                            status=models.Status.AVAILABLE)  

    if category_slug:
        category = get_object_or_404(models.Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'products' : products,
        'category' : category,
        'categories' : categories,
        'query': query,
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
