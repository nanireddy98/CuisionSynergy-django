def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat
    elif 'lat' in request.GET:
        lat = request.GET['lat']
        lng = request.GET['lng']
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    else:
        return None
