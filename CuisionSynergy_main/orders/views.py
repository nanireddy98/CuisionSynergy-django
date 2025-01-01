from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import simplejson as json
from django.contrib.auth.decorators import login_required
import razorpay

from .forms import OrderForm
from marketplace.context_processors import get_cart_amounts
from .models import Order, Payment, OrderedFood
from marketplace.models import Cart
from .utils import get_order_number
from accounts.utils import send_notification_mail
from CuisionSynergy_main.settings import RZP_KEY_ID, RZP_KEY_SECRET

client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))


@login_required(login_url='login')
def place_order(request):
    cartitems = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cartitems.count()
    if cart_count <= 0:
        return redirect('marketplace')

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
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = get_order_number(order.id)
            order.save()

            # razorpay payment
            data = {
                "amount": float(order.total)*100,
                "currency": "INR",
                "receipt": "receipt #"+order.order_number,
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
                'rzp_amount': float(order.total)*100,
                'RZP_KEY_ID': RZP_KEY_ID
            }
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)
    return render(request, "orders/place_order.html")


@login_required(login_url='login')
def payments(request):
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
        # return HttpResponse("Payment Saved")

        # update the Order model
        order.payment = payment
        order.is_ordered = True
        order.save()
        # return HttpResponse("Order Updated")

        # move the cart items to ordered food model
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
        # return HttpResponse("Ordered Food Saved")

        # Send Order Confirmation email to customer
        mail_subject = "Thankyou for Ordering With Us"
        mail_template = 'orders/order_confirmation_email_customer.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email
        }
        send_notification_mail(mail_subject, mail_template, context)
        # return HttpResponse("Ordered Food Saved and Email Sen To Customer")

        # Send Order Received email to vendor
        mail_subject = "You have Received a New Order"
        mail_template = 'orders/order_received_email_vendor.html'
        to_emails = []
        for i in cartitems:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)
        context = {
            'user': request.user,
            'order': order,
            'to_email': to_emails
        }
        send_notification_mail(mail_subject, mail_template, context)
        # return HttpResponse("Ordered Food Saved and Email Sent To Vendor")

        # clear cart if payment is Success
        cartitems.delete()

        # return Back to ajax with the status success or Failure
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)
    return HttpResponse("Payments")


def order_complete(request):
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
