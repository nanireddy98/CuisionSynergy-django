import json

from django.db import models
from accounts.models import User
from menu.models import FoodItem
from vendor.models import Vendor

request_object = ''


class Payment(models.Model):
    """Payment model to handle payment information for orders"""
    # Defining payment methods available
    PAYMENT_METHOD = (
        ('PayPal', 'PayPal'),
        ('RazorPay', 'RazorPay'),  # Only for Indian Students.
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)  # Unique transaction ID
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    """Order model to handle customer orders"""
    # Possible statuses for the order
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    vendors = models.ManyToManyField(Vendor, blank=True)  # Vendors associated with the order
    order_number = models.CharField(max_length=20)  # Unique order number
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    total = models.FloatField()

    # JSONField to store tax data in a specific format
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}", null=True)
    total_data = models.JSONField(blank=True, null=True)  # Store detailed total data for vendors

    total_tax = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Concatenate first name and last name
    @property
    def name(self):
        """Property to concatenate first and last names"""
        return f'{self.first_name} {self.last_name}'

    def order_placed_to(self):
        """Method to return the vendors associated with the order as a string"""
        return ", ".join([str(i) for i in self.vendors.all()])

    def get_total_by_vendor(self):
        """calculate and return total and tax data for a specific vendor"""
        vendor = Vendor.objects.get(user=request_object.user)
        subtotal = 0
        tax = 0
        tax_dict = {}
        if self.total_data:
            total_data = json.loads(self.total_data)  # Parse the total data from JSON
            data = total_data.get(str(vendor.id))  # Get vendor-specific dat
            print(data)
            for k, v in data.items():
                subtotal += float(k)
                v = v.replace("'", '"')
                v = json.loads(v)
                tax_dict.update(v)
                print(tax_dict)
                # Calculate tax based on the structure {'CGST': {'14.00': '84.00'}, 'SGST': {'9.00': '54.00'}}
                for i in v:
                    for j in v[i]:
                        tax += float(v[i][j])
        grand_total = float(subtotal) + float(tax)
        context = {
            'subtotal': subtotal,
            'tax_data': tax_dict,
            'grand_total': grand_total
        }
        return context

    def __str__(self):
        """Return the order number as string representation"""
        return self.order_number


class OrderedFood(models.Model):
    """OrderedFood model to represent items ordered in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the food title as string representation"""
        return self.fooditem.food_title
