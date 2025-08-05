from django.utils.html import MAX_URL_LENGTH
from rest_framework import serializers
from django.conf import settings
from django.shortcuts import render
from accounts.models import Account
from coupons.models import Coupon
from orders.models import Order, OrderItem, OrderPay
from store.models import Category, Product
from django.utils import timezone


# User = settings.AUTH_USER_MODEL



# 1- Serializers related to accounts 

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'password')
        
        extra_kwargs = {
            'first_name' : {'required' : True, 'allow_blank' : False},
            'last_name' : {'required' : True, 'allow_blank' : False},
            'email' : {'required' : True, 'allow_blank' : False},
            'phone_number' : {'required' : True, 'allow_blank' : False, 'max_length' : 11},
            'country' : {'required' : True, 'allow_blank' : False},
            'password' : {'required' : True, 'allow_blank' : False, 'min_length' : 8},
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'country', 'password')
       
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)



class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def validate_email(self, value):
        from django.contrib.auth.models import User
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email exists")
        return value
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, required=True)
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)





# 2- serilaizers related to products
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'image', 'description', 'price', 'status']






# 3- serilaizers related to orders
class OrderCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']




class MyOrdersSerializer(serializers.ModelSerializer):
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['order_id', 'paid', 'created_at', 'total_cost']

    def get_total_cost(self, obj):
        return obj.get_total_cost()



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')  # adjust if your product field has a different name
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['product', 'price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.get_cost()




class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['order_id', 'first_name', 'last_name', 'email', 'address',
                  'city', 'postal_code', 'paid', 'created_at', 'total_cost', 'items']

    def get_total_cost(self, obj):
        return obj.get_total_cost()




class OrderPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPay
        fields = ['order', 'pay_phone', 'pay_image']

    def validate_pay_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("The phone must contain digits only.")

        if len(value) != 11:
            raise serializers.ValidationError("The phone length must be exactly 11 digits.")

        valid_prefixes = ["010", "011", "012", "015"]
        if value[:3] not in valid_prefixes:
            raise serializers.ValidationError(f"The phone must start with one of: {', '.join(valid_prefixes)}")

        return value



# 4- serilaizers related to cart

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 51)]

class CartAddProductSerializer(serializers.Serializer):
    quantity = serializers.ChoiceField(choices=PRODUCT_QUANTITY_CHOICES)

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        internal_data['quantity'] = int(internal_data['quantity'])  # Ensure int
        return internal_data


# 5- serilaizers related to coupon
class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code__iexact=value.strip())
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")

        now = timezone.now()
        if not coupon.active:
            raise serializers.ValidationError("This coupon is not active.")
        if coupon.valid_from > now:
            raise serializers.ValidationError("This coupon is not yet valid.")
        if coupon.valid_to < now:
            raise serializers.ValidationError("This coupon has expired.")

        # Save the validated coupon for use in `validated_data`
        self.coupon = coupon
        return value

    def validate(self, attrs):
        # Include coupon data in the validated_data to return
        attrs['coupon'] = {
            'code': self.coupon.code,
            'discount': self.coupon.discount,
            'slug': self.coupon.slug,
            'valid_from': self.coupon.valid_from,
            'valid_to': self.coupon.valid_to,
        }
        return attrs













