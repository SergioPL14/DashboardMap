import json

import pd as pd
import requests
import yaml
import pandas as pd
from geopy.geocoders import Nominatim

# Site -> Location + State -> Address (coordinates)

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/auth"

json_body = {'username': config['user'], 'password': config['pwd']}

response = requests.post(api_url, json_body)
print(response.json()['sessionId'])

headers = {'Authorization': response.json()['sessionId']}

# LOCATIONS
# api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/location__v"
# json_body = {'username': config['user'], 'password': config['pwd']}
# response = requests.get(api_url, json_body, headers=headers)
#
# print(response.json()['data'])
# print(response.json()['data'][1]['id'])

# STUDIES
# api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/study__v"
# json_body = {'username': config['user'], 'password': config['pwd']}
# response = requests.get(api_url, json_body, headers=headers)
# print(response.json()['data'])

# STUDY COUNTRIES
# api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/study_country__v"
# json_body = {'username': config['user'], 'password': config['pwd']}
# response = requests.get(api_url, json_body, headers=headers)
# print(response.json()['data'])

# SITES
api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/site__v"
json_body = {'username': config['user'], 'password': config['pwd']}
response = requests.get(api_url, json_body, headers=headers)
print(response.json())

################## 1 SITES
df = pd.DataFrame(response.json()['data'])

################## 2 SITES ATTRIBUTES
df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'site_status__v'])
for id in df['id']:
    api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/site__v/" + id
    json_body = {'username': config['user'], 'password': config['pwd']}
    response = requests.get(api_url, json_body, headers=headers)
    df2 = pd.concat([df2, pd.DataFrame(response.json()['data'])[['id', 'location__v', 'status__v', 'state__v', 'site_status__v']]], ignore_index=True)

df = pd.merge(df, df2, on="id")

################## 3 LOCATIONS
df3 = pd.DataFrame(columns=['id', 'address_line_1__clin', 'latitude', 'longitude'])
geolocator = Nominatim(user_agent="dashboardmap")
for loc in df['location__v']:
    api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/location__v/" + loc
    json_body = {'username': config['user'], 'password': config['pwd']}
    response = requests.get(api_url, json_body, headers=headers).json()['data']
    lat = geolocator.geocode(response['address_line_1__clin']).latitude
    lon = geolocator.geocode(response['address_line_1__clin']).longitude
    df_aux = pd.DataFrame(response)[["id", "address_line_1__clin"]]
    df_aux[["latitude", "longitude"]] = [lat, lon]
    df3 = pd.concat(
        [df3, df_aux], ignore_index=True)

df3=df3.rename(columns={'id': 'location__v'})
df = pd.merge(df, df3, on="location__v")

print(df)


# 1 Sites
# 2 Interar en sites para obtener Location, Status (state? sit_state?), URL
# URL: https://candidate-tech-services---sergio.veevavault.com/ui/#t/0TB000000000K15/0ST/0ST000000001001
# URL: https://candidate-tech-services---sergio.veevavault.com/ui/#t/0TB000000000K15/0SC/0SC000000002002
# 3 Iterar en locations para tener coordenadas
# 4 Montar DF
