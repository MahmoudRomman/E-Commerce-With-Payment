from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from . import models
from cart import forms as cart_forms
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.



from django.utils.translation import gettext as _

def my_view(request):
    message = _("This is a translatable string")



def home(request):
    category = None
    query = request.GET.get('q', '')  # Get query string from ?q=...

    if query:
        products = models.Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            status=models.Status.AVAILABLE
        )
    else:
        products = models.Product.objects.filter(
            status=models.Status.AVAILABLE
        ).order_by('?')[:12]  # 12 random products

    context = {
        'products': products,
        'category': category,
        'query': query,
    }

    return render(request, 'store/home.html', context)






def products(request, category_slug=None):
    category = None
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)  # Get page number from query string
    cache_key = f'products_{category_slug or "all"}_{query}'

    # Try to get products from cache
    cached_products = cache.get(cache_key)

    if cached_products is None:
        products_queryset = models.Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            status=models.Status.AVAILABLE
        )

        if category_slug:
            category = get_object_or_404(models.Category, slug=category_slug)
            products_queryset = products_queryset.filter(category=category)

        # Cache list of products
        cached_products = list(products_queryset)
        cache.set(cache_key, cached_products, timeout=60 * 30)  # 30 min

    # Apply pagination
    paginator = Paginator(cached_products, 12)  # 12 products per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'category': category,
        'query': query,
    }
    return render(request, 'store/products.html', context)




def product_detail(request, slug):
    cache_key = f"product_{slug}"
    product = cache.get(cache_key)
    if product is None:
        try:
            product = models.Product.objects.get(slug=slug, status=models.Status.AVAILABLE)  #type: ignore
            cache.set(cache_key, product, timeout = 60 * 30)
        except ObjectDoesNotExist:
            messages.error(request, 'Sorry, This product is not found!')
            return redirect('store:products')  # redirect to the url page that you want
    
    form = cart_forms.CartAddProductForm()
    context = {
        'product' : product,
        'form' : form,
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
