from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from . import serializers
from accounts.models import Account
from coupons.models import Coupon
from orders.models import Order, OrderItem, OrderPay
from store.models import Category, Product
from store import models as store_models
from django.db.models import Q
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from orders import tasks as orders_tasks 
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone






# 1- Views related to account app - register, login, logout, activate account, profile
@api_view(['POST'])
def register(request):
    serializer = serializers.SignUpSerializer(data=request.data)
    if serializer.is_valid():
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        email = serializer.validated_data['email']
        phone_number = serializer.validated_data['phone_number']
        country = serializer.validated_data['country']
        password = serializer.validated_data['password']
        username = email.split('@')[0]

        if not Account.objects.filter(email=email).exists():
            try:
                user = Account.objects.create_user(
                    first_name = first_name,
                    last_name = last_name,
                    email = email, username = username,
                    country = country, password = password
                )

                user.phone_number = phone_number
                user.save()


                token,_ = Token.objects.get_or_create(user=user)
                return Response({
                    "message": "User created successfully",
                    "token": token.key
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"Message: " : "This email is already exists!"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def login(request):
    serializer = serializers.LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.data['email']
        password = serializer.data['password']
        try:
            user = Account.objects.get(email=email)
            user = authenticate(email=email, password=password)
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'message': 'Logged in successfully',
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid Password'}, status=status.HTTP_401_UNAUTHORIZED)
        except ObjectDoesNotExist:
            return Response({'Error: ' : "The email you entered is invalid or not matching you!"})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# 2- views related to the store app, home, products and product_details
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def home(request):
    query = request.GET.get('q', '')

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            status=store_models.Status.AVAILABLE
        )
    else:
        products = Product.objects.filter(
            status=store_models.Status.AVAILABLE
        ).order_by('?')[:12]

    serializer = serializers.ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)






@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def products(request, category_slug=None):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    cache_key = f'products_{category_slug or "all"}_{query}'

    # Try to get from cache
    cached_products = cache.get(cache_key)

    if cached_products is None:
        products_queryset = Product.objects.filter(status=store_models.Status.AVAILABLE)

        if query:
            products_queryset = products_queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products_queryset = products_queryset.filter(category=category)

        cached_products = list(products_queryset)
        cache.set(cache_key, cached_products, timeout=60 * 30)

    # Apply pagination
    paginator = Paginator(cached_products, 12)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        return Response({'error': 'No more products'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = serializers.ProductSerializer(products_page, many=True)
    return Response({
        'results': serializer.data,
        'page': int(page),
        'total_pages': paginator.num_pages,
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail(request, slug):
    cache_key = f"product_{slug}"
    product = cache.get(cache_key)
    if product is None:
        product = get_object_or_404(Product, slug=slug, status=store_models.Status.AVAILABLE)  #type: ignore
        cache.set(cache_key, product, timeout = 60 * 30)
    
    serializer = serializers.ProductSerializer(product, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)





# 3- views related to the orderscart app, including adding/removing items from the cart, applying a coupon, and paying for an order
@api_view(['POST'])
def add_to_cart(request, product_slug):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, slug=product_slug)
    product_key = str(product_slug)
    price = product.price  # Decimal
    image_url = product.image.url if product.image else ''

    serializer = serializers.CartAddProductSerializer(data=request.data)

    if serializer.is_valid():
        quantity = int(serializer.validated_data.get('quantity', 1))
    else:
        quantity = 1  # Default fallback if invalid or no quantity sent

    # Add or update item in cart
    if product_key in cart:
        cart[product_key]['quantity'] += quantity
    else:
        cart[product_key] = {
            'quantity': quantity,
            'name': product.name,
            'price': str(price),
            'image': image_url
        }

    # Update total price
    total_quantity = cart[product_key]['quantity']
    cart[product_key]['total_price'] = str(price * total_quantity)

    # Save back to session
    request.session['cart'] = cart

    return Response({
        "message": "Item added to cart.",
        "product": product_key,
        "quantity": total_quantity,
        "product_name": product.name,
        "product_price": str(price),
        "total_price": cart[product_key]['total_price'],
        "image": image_url,
    }, status=status.HTTP_200_OK)





@api_view(['POST'])
def remove_from_cart(request, product_slug):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, slug=product_slug)
    product_key = str(product_slug)

    if product_key not in cart:
        return Response({"message": "This item is not in your cart."}, status=status.HTTP_400_BAD_REQUEST)

    if cart[product_key]['quantity'] > 1:
        cart[product_key]['quantity'] -= 1
        cart[product_key]['total_price'] = str(product.price * cart[product_key]['quantity'])
        request.session['cart'] = cart

        return Response({
            "message": "Item quantity updated.",
            "product": product_key,
            "quantity": cart[product_key]['quantity'],
            "product_name": cart[product_key]['name'],
            "product_price": cart[product_key]['price'],
            "total_price": cart[product_key]['total_price'],
            "image": cart[product_key]['image'],
        }, status=status.HTTP_200_OK)
    else:
        del cart[product_key]
        if cart:
            request.session['cart'] = cart
        else:
            request.session.pop('cart', None)

        return Response({"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def remove_single_item_from_cart(request, product_slug):
    cart = request.session.get('cart', {})
    product_key = str(product_slug)

    if product_key not in cart:
        return Response({"message": "This item is not in your cart."}, status=status.HTTP_400_BAD_REQUEST)

    # Remove item
    del cart[product_key]

    # Update session
    if cart:
        request.session['cart'] = cart
    else:
        request.session.pop('cart', None)

    return Response({"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
def get_coupon_instance(request):
    coupon_slug = request.session.get('coupon_slug', {})
    if coupon_slug:
        coupon = get_object_or_404(Coupon, slug=coupon_slug)
        return coupon
    return None




def get_discount_value(request):
    coupon = get_coupon_instance(request)
    if coupon:
        cart = request.session.get('cart', {})
        total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
        res = (coupon.discount / Decimal(100)) * total_cart_price
        return res
    return Decimal(0)



def get_final_cart_cost(request):
    dis_val = get_discount_value(request)
    if dis_val:
        cart = request.session.get('cart', {})
        total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
        final_price = Decimal(total_cart_price - dis_val)
        request.session['get_final_price_after_coupon'] = float(final_price)

    else:
        request.session['get_final_price_after_coupon'] = float(0)



@api_view(['POST'])
def apply_coupon(request):
    serializer = serializers.ApplyCouponSerializer(data=request.data)

    now = timezone.now()
    if serializer.is_valid():
        code = serializer.validated_data['code']

        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                active=True
            )
            request.session['coupon_slug'] = coupon.slug
        except ObjectDoesNotExist:
            request.session['coupon_slug'] = None



def round_decimal(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@api_view(['GET'])
def view_cart(request):
    cart = request.session.get('cart', {})

    get_final_cart_cost(request)  # calculate & store in session
    get_final_price_after_coupon = request.session.get('get_final_price_after_coupon', 0)

    if not isinstance(get_final_price_after_coupon, Decimal):
        get_final_price_after_coupon = Decimal(get_final_price_after_coupon)

    total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())
    total_cart_price = round_decimal(total_cart_price)
    get_final_price_after_coupon = round_decimal(get_final_price_after_coupon)

    if get_final_price_after_coupon == Decimal("0.00"):
        savings = Decimal("0.00")
    else:
        savings = round_decimal(total_cart_price - get_final_price_after_coupon)

    json = {
        'cart': cart,
        'total_cart_price': total_cart_price,
        'get_final_price_after_coupon': get_final_price_after_coupon,
        'savings': savings,
    }

    return Response(json, status=status.HTTP_200_OK)





# 4- views related to the orders app, including creating an order, viewing order details, and paying for an order

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_order(request):
    cart = request.session.get('cart', {})
    coupon_slug = request.session.get('coupon_slug')

    if not cart:
        return Response({"message": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    # Inject the authenticated user into serializer data
    data = request.data.copy()
    data['user'] = request.user.id

    serializer = serializers.OrderCreationSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Save order
    order = serializer.save()

    # Add order items
    for slug, item in cart.items():
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response(
                {"message": f"Unavailable product with slug: {slug}"},
                status=status.HTTP_404_NOT_FOUND
            )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=item['total_price']
        )

    # Clear cart and coupon from session
    request.session.pop('cart', None)
    request.session.pop('coupon_slug', None)

    # Send confirmation email asynchronously
    orders_tasks.send_order_confirmation_email.delay(order.id)

    total_cart_price = sum(Decimal(item['total_price']) for item in cart.values())

    return Response({
        "message": "Order created successfully.",
        "order_id": order.order_id,
        "cart_details": cart,
        "cart_total_price": str(total_cart_price)
    }, status=status.HTTP_201_CREATED)




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    serializer = serializers.MyOrdersSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    order = get_object_or_404(Order, user=request.user, order_id=order_id)
    serializer = serializers.OrderDetailSerializer(order, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['POST'])  # should be POST since you're submitting data
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def order_pay_by_VF(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Prevent duplicate payment
    if OrderPay.objects.filter(order=order).exists():
        return Response({"error": "Payment has already been submitted for this order."}, status=400)

    # Include the order ID in the serializer data
    data = request.data.copy()
    data['order'] = order.id

    serializer = serializers.OrderPaySerializer(data=data)
    if serializer.is_valid():
        serializer.save()

        # Mark the order as paid
        order.paid = True
        order.save()

        return Response({"message": "Payment submitted successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])  # should be POST since you're submitting data
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def payment_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    serializer = serializers.OrderDetailSerializer(order, many=False)
    orders_tasks.send_order_pdf.delay(order.id) 
    return Response(serializer.data, status=status.HTTP_200_OK)

















