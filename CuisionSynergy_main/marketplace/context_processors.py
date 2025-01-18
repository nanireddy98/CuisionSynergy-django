from .models import Cart, FoodItem, Tax


def get_cart_counter(request):
    """Calculate the total quantity of items in the user's cart."""
    cart_count = 0
    try:
        # Fetch all cart items for the logged-in user
        cart_items = Cart.objects.filter(user=request.user)
        if cart_items:
            # Sum the quantities of all items in the cart
            for cartitem in cart_items:
                cart_count += cartitem.quantity
        else:
            cart_count = 0
    except:
        cart_count = 0
    return dict(cart_count=cart_count)


def get_cart_amounts(request):
    """ Calculate the subtotal, tax, and grand total amounts for the user's cart."""
    sub_total = 0
    tax = 0
    grand_total = 0
    tax_dict = {}

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Fetch all cart items for the user
        cartitem = Cart.objects.filter(user=request.user)
        for item in cartitem:
            # Get the related food item and calculate the subtotal
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            sub_total += (fooditem.price * item.quantity)

        # Fetch active tax rates
        get_tax = Tax.objects.filter(is_active=True)
        for tax_record in get_tax:
            # Calculate the tax amount for each active tax rate
            tax_type = tax_record.tax_type
            tax_percentage = tax_record.tax_percentage
            tax_amount = round((tax_percentage * sub_total) / 100, 2)
            tax_dict.update({
                tax_type: {
                    str(tax_percentage): tax_amount
                }
            })

        # Calculate total tax amount
        tax = sum(x for key in tax_dict.values() for x in key.values())
        # Calculate the grand total (subtotal + tax)
        grand_total = tax + sub_total
    return dict(sub_total=sub_total, tax=tax, grand_total=grand_total, tax_dict=tax_dict)
