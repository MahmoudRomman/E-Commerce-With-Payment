
from store.models import Category
def cart_item_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    return {
        'cart_item_count': total_items
    }



def get_categories(request):
    categories = Category.objects.all() #type: ignore

    return {
        'categories' : categories,
    }
