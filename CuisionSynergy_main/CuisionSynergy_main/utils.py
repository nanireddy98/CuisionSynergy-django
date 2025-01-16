def get_or_set_current_location(request):
    """
    Retrieves the current location (latitude and longitude) from the session or GET parameters.
    If not found in the session, it attempts to fetch from the GET parameters and store them in the session.
    """
    # Check if the location is already stored in the session
    if 'lat' in request.session and 'lng' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat
    # If not found in session, check GET parameters and store them in the session
    elif 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET['lat']
        lng = request.GET['lng']
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    return None
