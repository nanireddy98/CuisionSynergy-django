from .models import Cart, FoodItem, Tax


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
    tax_dict = {}
    if request.user.is_authenticated:
        cartitem = Cart.objects.filter(user=request.user)
        for item in cartitem:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            sub_total += (fooditem.price * item.quantity)
        get_tax = Tax.objects.filter(is_active=True)
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * sub_total) / 100, 2)
            tax_dict.update({
                tax_type: {
                    str(tax_percentage): tax_amount
                }
            })
        tax = sum(x for key in tax_dict.values() for x in key.values())
        grand_total = tax + sub_total
    return dict(sub_total=sub_total, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
