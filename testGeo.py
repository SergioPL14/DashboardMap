from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="dashboardmap")
location = geolocator.geocode("1-16-10 Shibaura, Minato-ku, Tokyo")
print(location.address)
print((location.latitude, location.longitude))
