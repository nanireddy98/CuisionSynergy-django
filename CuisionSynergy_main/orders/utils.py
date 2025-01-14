import datetime
import simplejson as json


def get_order_number(pk):
    current_date_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    order_number = current_date_time + str(pk)
    return order_number


def order_total_by_vendor(order,vendor_id):
    total_data = json.loads(order.total_data)
    data = total_data.get(str(vendor_id))
    subtotal = 0
    tax = 0
    tax_dict = {}

    for k, v in data.items():
        subtotal += float(k)
        print(subtotal)
        v = v.replace("'", '"')
        v = json.loads(v)
        tax_dict.update(v)
        print(tax_dict)
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
