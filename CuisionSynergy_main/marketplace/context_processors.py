from .models import Cart, FoodItem


def get_cart_counter(request):
    cart_count = 0
    try:
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items:
            for cartitem in cart_items:
                cart_count += cartitem.quantity
        else:
            cart_count = 0
    except:
        cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    sub_total = 0
    tax = 0
    grand_total = 0
    if request.user.is_authenticated:
        cartitem = Cart.objects.filter(user=request.user)
        for item in cartitem:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            sub_total += (fooditem.price * item.quantity)
        grand_total = tax + sub_total
    print(grand_total)
    return dict(sub_total=sub_total, tax=tax, grand_total=grand_total)
