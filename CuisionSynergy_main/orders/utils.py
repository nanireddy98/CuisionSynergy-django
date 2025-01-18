import datetime
import simplejson as json


def get_order_number(pk):
    """generate a unique order number based on the current timestamp and order pk (primary key)"""
    current_date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    order_number = current_date_time + str(pk)
    return order_number


def order_total_by_vendor(order,vendor_id):
    """calculate the total for an order by vendor, including subtotals, tax, and grand total"""
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal = 0
    tax = 0
    tax_dict = {}

    # Iterate through the vendor data to calculate the subtotal and tax
    for k, v in data.items():
        subtotal += float(k)
        v = v.replace("'", '"')  # Replace single quotes with double quotes to ensure valid JSON format
        v = json.loads(v)
        tax_dict.update(v)

        # Iterate through the tax data to calculate the total tax
        for i in v:
            for j in v[i]:
                tax += float(v[i][j])

    # Calculate the grand total by adding the subtotal and tax
    grand_total = float(subtotal) + float(tax)

    # Return a context dictionary with the calculated values
    context = {
        'subtotal': subtotal,
        'tax_data': tax_dict,
        'grand_total': grand_total
    }
    return context
