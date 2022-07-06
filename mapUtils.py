import requests
import yaml
import pandas as pd
from geopy.geocoders import Nominatim


def getSessionId(config):
    api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/auth"
    json_body = {'username': config['user'], 'password': config['pwd']}
    response = requests.post(api_url, json_body)
    return response.json()['sessionId']


def getSites(json_sessionId, config):
    headers = {'Authorization': json_sessionId}
    api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/site__v"
    json_body = {'username': config['user'], 'password': config['pwd']}
    response = requests.get(api_url, json_body, headers=headers)
    return pd.DataFrame(response.json()['data'])


def getSitesAttributes(json_sessionId, df, config):
    headers = {'Authorization': json_sessionId}
    df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'site_status__v', 'url'])
    for id in df['id']:
        api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/site__v/" + id
        json_body = {'username': config['user'], 'password': config['pwd']}
        response = requests.get(api_url, json_body, headers=headers)
        df2 = pd.concat([df2, pd.DataFrame(response.json()['data'])[
            ['id', 'location__v', 'status__v', 'state__v', 'site_status__v']]], ignore_index=True)
    df2['url'] = "https://" + config['vault_domain_name'] + "/ui/#t/0TB000000000K15/0ST/" + df2['id']
    return pd.merge(df, df2, on="id")


def getLocations(json_sessionId, df, config):
    headers = {'Authorization': json_sessionId}
    df3 = pd.DataFrame(columns=['id', 'address_line_1__clin', 'latitude', 'longitude'])
    geolocator = Nominatim(user_agent="dashboardmap")
    for loc in df['location__v']:
        api_url = "https://" + config['vault_domain_name'] + "/api/" + config[
            'version'] + "/vobjects/location__v/" + loc
        json_body = {'username': config['user'], 'password': config['pwd']}
        response = requests.get(api_url, json_body, headers=headers).json()['data']
        lat = geolocator.geocode(response['address_line_1__clin']).latitude
        lon = geolocator.geocode(response['address_line_1__clin']).longitude
        df_aux = pd.DataFrame(response)[["id", "address_line_1__clin"]]
        df_aux[["latitude", "longitude"]] = [lat, lon]
        df3 = pd.concat(
            [df3, df_aux], ignore_index=True)
    df3 = df3.rename(columns={'id': 'location__v'})
    return pd.merge(df, df3, on="location__v")


def getMapInfo():
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    json_sessionId = getSessionId(config)
    sites = getSites(json_sessionId, config)
    sitesAttributes = getSitesAttributes(json_sessionId, sites, config)
    mapInfo = getLocations(json_sessionId, sitesAttributes, config)
    return mapInfo

################## 1 SITES
# df = pd.DataFrame(response.json()['data'])

################## 2 SITES ATTRIBUTES
# df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'site_status__v'])
# for id in df['id']:
#     api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/site__v/" + id
#     json_body = {'username': config['user'], 'password': config['pwd']}
#     response = requests.get(api_url, json_body, headers=headers)
#     df2 = pd.concat(
#         [df2, pd.DataFrame(response.json()['data'])[['id', 'location__v', 'status__v', 'state__v', 'site_status__v']]],
#         ignore_index=True)
#
# # df = pd.merge(df, df2, on="id")
#
# ################## 3 LOCATIONS
# df3 = pd.DataFrame(columns=['id', 'address_line_1__clin', 'latitude', 'longitude'])
# geolocator = Nominatim(user_agent="dashboardmap")
# for loc in df['location__v']:
#     api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/location__v/" + loc
#     json_body = {'username': config['user'], 'password': config['pwd']}
#     response = requests.get(api_url, json_body, headers=headers).json()['data']
#     lat = geolocator.geocode(response['address_line_1__clin']).latitude
#     lon = geolocator.geocode(response['address_line_1__clin']).longitude
#     df_aux = pd.DataFrame(response)[["id", "address_line_1__clin"]]
#     df_aux[["latitude", "longitude"]] = [lat, lon]
#     df3 = pd.concat(
#         [df3, df_aux], ignore_index=True)
#
# df3 = df3.rename(columns={'id': 'location__v'})
# # df = pd.merge(df, df3, on="location__v")
#
# print(df)

# 1 Sites
# 2 Interar en sites para obtener Location, Status (state? sit_state?), URL
# URL: https://candidate-tech-services---sergio.veevavault.com/ui/#t/0TB000000000K15/0ST/0ST000000001001
# URL: https://candidate-tech-services---sergio.veevavault.com/ui/#t/0TB000000000K15/0SC/0SC000000002002
# 3 Iterar en locations para tener coordenadas
# 4 Montar DF
