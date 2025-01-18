let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);

}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({'address': address}, function(results, status){
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat();
            var longitude = results[0].geometry.location.lng();

            $('#id_latitude').val(latitude);
            $('#id_longitude').val(longitude);

            $('#id_address').val(address);
        }
    });
    // loop through the address components and assign other address data
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name);
            }
            // get state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name);
            }
            // get city
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name);
            }
            // get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pin_code').val(place.address_components[i].long_name);
            }else{
                $('#id_pin_code').val("");
            }
        }
    }
}

$(document).ready(function () {

    // Utility function to update the cart amounts and display
    function updateCartAmounts(cart_amount) {
        $('#cart_counter').html(cart_amount.cart_count);
        $('#subtotal').html(cart_amount.sub_total);
        $('#total').html(cart_amount.grand_total);

        for (let key1 in cart_amount.tax_dict) {
            for (let key2 in cart_amount.tax_dict[key1]) {
                $('#tax-' + key1).html(cart_amount.tax_dict[key1][key2]);
            }
        }
    }

    // Utility function to handle common ajax response actions
    function handleAjaxResponse(response, callback) {
        if (response.status == 'login_required') {
            swal(response.message, '', 'info').then(function () {
                window.location = '/login';
            });
        } else if (response.status == 'failed') {
            swal(response.message, '', 'error');
        } else {
            callback(response);
        }
    }

    // Event listener for the "Add to Cart(+)" button
    $('.add_to_cart').on('click', function (e) {
        e.preventDefault();

        let food_id = $(this).data('id');
        let url = $(this).data('url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                handleAjaxResponse(response, function (res) {
                    $('#qty-' + food_id).html(res.qty);
                    updateCartAmounts(res.cart_amount);
                });
            }
        });
    });

    // Place cart item qty on load
    $('.item_qty').each(function () {
        let qty = $(this).data('qty');
        $(this).html(qty);
    });

    // Event listener for the "Decrease Cart(-)" button
    $('.decrease_cart').on('click', function (e) {
        e.preventDefault();

        let food_id = $(this).data('id');
        let url = $(this).data('url');
        let cart_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                handleAjaxResponse(response, function (res) {
                    $('#qty-' + food_id).html(res.qty);
                    updateCartAmounts(res.cart_amount);

                    if (window.location.pathname == '/cart/') {
                        removeCartItem(res.qty, cart_id);
                        checkEmptyCart();
                    }
                });
            }
        });
    });

    // Event listener for the "Delete Cart" button
    $('.delete_cart').on('click', function (e) {
        e.preventDefault();

        let cart_id = $(this).data('id');
        let url = $(this).data('url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                handleAjaxResponse(response, function (res) {
                    swal(res.status, res.message, 'success');
                    updateCartAmounts(res.cart_amount);

                    if (window.location.pathname == '/cart/') {
                        removeCartItem(0, cart_id);
                        checkEmptyCart();
                    }
                });
            }
        });
    });

    // Function to remove CartItem if qty <= 0
    function removeCartItem(CartItemQty, cart_id) {
        if (CartItemQty <= 0) {
            $('#cart-item-' + cart_id).remove();
        }
    }

    // Function to check if the cart is empty
    function checkEmptyCart() {
        if ($('#cart_counter').html() == 0) {
            $('#empty-cart').show();
        }
    }

    // Event listener for adding Opening Hours for Vendor/Restaurant
    $('.add_hour').on('click', function (e) {
        e.preventDefault();

        let day = $('#id_day').val();
        let from_hour = $('#id_from_hour').val();
        let to_hour = $('#id_to_hour').val();
        let is_closed = $('#id_is_closed').is(':checked');
        let csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        let url = $('#add_open_hour').val();

        if ((is_closed || (day && from_hour && to_hour))) {
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    day: day,
                    from_hour: from_hour,
                    to_hour: to_hour,
                    is_closed: is_closed ? 'True' : 'False',
                    csrfmiddlewaretoken: csrf_token
                },
                success: function (response) {
                    if (response.status == 'success') {
                        let html = `<tr id="hour-${response.id}">
                                        <td><b>${response.day}</b></td>
                                        <td>${response.is_closed == 'Closed' ? 'Closed' : response.from_hour + ' - ' + response.to_hour}</td>
                                        <td><a href="#" class="remove_hour" data-url="/vendor/opening-hour/remove/${response.id}/">Remove</a></td>
                                    </tr>`;
                        $('.opening_hours').append(html);
                        $('#opening_hours')[0].reset();
                    } else {
                        swal(response.message, '', 'error');
                    }
                }
            });
        } else {
            swal("Please fill all the fields", "", "info");
        }
    });

    // Remove the Opening Hours
    $(document).on('click', '.remove_hour', function (e) {
        e.preventDefault();

        let url = $(this).data('url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (response.status == 'success') {
                    $('#hour-' + response.id).remove();
                }
            }
        });
    });

});
