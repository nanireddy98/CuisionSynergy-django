from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import simplejson as json
from django.contrib.auth.decorators import login_required
import razorpay
from django.contrib.sites.shortcuts import get_current_site

from .forms import OrderForm
from marketplace.context_processors import get_cart_amounts
from .models import Order, Payment, OrderedFood
from marketplace.models import Cart, FoodItem, Tax
from .utils import get_order_number, order_total_by_vendor
from accounts.utils import send_notification_mail
from CuisionSynergy_main.settings import RZP_KEY_ID, RZP_KEY_SECRET

client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))


@login_required(login_url='login')
def place_order(request):
    """Handles order placement."""
    cartitems = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cartitems.count()
    if cart_count <= 0:
        return redirect('marketplace')

    # Get unique vendor IDs from the cart items
    vendor_ids = list({i.fooditem.vendor.id for i in cartitems})

    # {"Vendor_id": {"subtotal":{"tax_type":{"tax_percentage": "tax_amount"}}}}
    # calculate subtotal
    get_tax = Tax.objects.filter(is_active=True)
    subtotal = 0
    k = {}
    total_data = {}

    # Calculate subtotal and tax data for each vendor
    for i in cartitems:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendor_ids)
        v_id = fooditem.vendor.id

        # Calculate subtotal for each vendor
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (i.fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (i.fooditem.price * i.quantity)
            k[v_id] = subtotal

        # Calculate tax data for the vendor
        tax_dict = {}
        for i in get_tax:
            tax_type = i.tax_type
            tax_percentage = i.tax_percentage
            tax_amount = round((tax_percentage * subtotal) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})

        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})

    sub_total = get_cart_amounts(request)['sub_total']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = get_order_number(order.id)
            order.vendors.add(*vendor_ids)
            order.save()

            # Razorpay payment integration
            data = {
                "amount": float(order.total) * 100,  # Convert to paise
                "currency": "INR",
                "receipt": "receipt #" + order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            rzp_order = client.order.create(data=data)
            rzp_order_id = rzp_order['id']

            context = {
                'order': order,
                'cartitems': cartitems,
                'rzp_order_id': rzp_order_id,
                'rzp_amount': float(order.total) * 100,
                'RZP_KEY_ID': RZP_KEY_ID
            }
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)
    return render(request, "orders/place_order.html")


@login_required(login_url='login')
def payments(request):
    """Handles payment confirmation."""
    # check if request is Ajax or Not
    if request.headers.get('x-requested-with') == "XMLHttpRequest" and request.method == "POST":
        # Store the Payment Details in payment model
        order_number = request.POST['order_number']
        transaction_id = request.POST['transaction_id']
        payment_method = request.POST['payment_method']
        status = request.POST['status']
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()

        # Update the order model with the payment details
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Transfer the cart items to the OrderedFood model
        cartitems = Cart.objects.filter(user=request.user)
        for item in cartitems:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity  # total amount
            ordered_food.save()

        # Send order confirmation email to the customer
        mail_subject = "Thankyou for Ordering With Us"
        mail_template = 'orders/order_confirmation_email_customer.html'
        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
            'ordered_food': ordered_food,
            'domain': get_current_site(request),
            'customer_subtotal': customer_subtotal,
            'tax_data': tax_data,
        }
        send_notification_mail(mail_subject, mail_template, context)

        # Send Order Received email to vendor
        mail_subject = "You have Received a New Order"
        mail_template = 'orders/order_received_email_vendor.html'
        to_emails = []
        for i in cartitems:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)

                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)

                context = {
                    'user': request.user,
                    'order': order,
                    'to_email': i.fooditem.vendor.user.email,
                    'ordered_food_to_vendor': ordered_food_to_vendor,
                    'vendor_subtotal': order_total_by_vendor(order, i.fooditem.vendor.id)['subtotal'],
                    'tax_data': order_total_by_vendor(order, i.fooditem.vendor.id)['tax_data'],
                    'vendor_grand_total': order_total_by_vendor(order, i.fooditem.vendor.id)['grand_total']
                }
                send_notification_mail(mail_subject, mail_template, context)

        # clear cart if payment is Success
        cartitems.delete()

        # return Back to ajax with the status success or Failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)


def order_complete(request):
    """Displays the order completion page."""
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        sub_total = 0
        for item in ordered_food:
            sub_total += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'taxdata': tax_data,
            'subtotal': sub_total
        }
        return render(request, "orders/order_complete.html", context)
    except:
        return redirect('home')
