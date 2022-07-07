from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="dashboardmap")
location = geolocator.geocode("Spain")
print(location.address)
print((location.latitude, location.longitude))
