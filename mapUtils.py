import requests
import yaml
import pandas as pd
from geopy.geocoders import Nominatim


def getSessionId(config, url):
    endpoint = url + "/auth"
    json_body = {'username': config['user'], 'password': config['pwd']}
    response = requests.post(endpoint, json_body)
    return response.json()['sessionId']


def getSites(sessionId, url):
    headers = {'Authorization': sessionId}
    endpoint = url + "/vobjects/site__v"
    response = requests.get(endpoint, headers=headers)
    return pd.DataFrame(response.json()['data'])


def getSitesAttributes(sessionId, df, config, url):
    headers = {'Authorization': sessionId}
    df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'site_status__v', 'country__v', 'url'])
    for id in df['id']:
        endpoint = url + "/vobjects/site__v/" + id
        response = requests.get(endpoint, headers=headers)
        df2 = pd.concat([df2, pd.DataFrame(response.json()['data'])[
            ['id', 'location__v', 'status__v', 'state__v', 'site_status__v', 'country__v']]], ignore_index=True)
    df2['url'] = "https://" + config['vault_domain_name'] + "/ui/#t/0TB000000000K15/0SI/" + df2['id']
    return pd.merge(df, df2, on="id")


def getLocations(sessionId, df, url):
    headers = {'Authorization': sessionId}
    df3 = pd.DataFrame(columns=['id', 'address_line_1__clin', 'latitude', 'longitude'])
    geolocator = Nominatim(user_agent="dashboardmap")
    for loc in df['location__v']:
        try:
            endpoint = url + "/vobjects/location__v/" + loc
            response = requests.get(endpoint, headers=headers).json()['data']
            df_aux = pd.DataFrame(response)[["id", "address_line_1__clin"]]
            lat = geolocator.geocode(response['address_line_1__clin']).latitude
            lon = geolocator.geocode(response['address_line_1__clin']).longitude
            df_aux[["latitude", "longitude"]] = [lat, lon]
            df3 = pd.concat(
                [df3, df_aux], ignore_index=True)
        except Exception as e:
            endpoint = url + "/vobjects/country__v/" + loc
            response = requests.get(endpoint, headers=headers).json()['data']
            df_aux = pd.DataFrame(response)[["id"]]
            lat = geolocator.geocode(response['name__v']).latitude
            lon = geolocator.geocode(response['name__v']).longitude
            df_aux[["latitude", "longitude"]] = [lat, lon]
            df3 = pd.concat(
                [df3, df_aux], ignore_index=True)
    df3 = df3.rename(columns={'id': 'location__v'})
    return pd.merge(df, df3, on="location__v")


def getSiteCountries(sessionId, df, config, url):
    headers = {'Authorization': sessionId}
    endpoint = url + "/vobjects/study_country__v"
    df_aux = pd.DataFrame(requests.get(endpoint, headers=headers).json()['data'])

    df4 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'country__v', 'url'])
    for id in df_aux['id']:
        endpoint = url + "/vobjects/study_country__v/" + id
        response = requests.get(endpoint, headers=headers)
        df4 = pd.concat([df4, pd.DataFrame(response.json()['data'])[
            ['id', 'status__v', 'state__v', 'country__v']]], ignore_index=True)
    df4['url'] = "https://" + config['vault_domain_name'] + "/ui/#t/0TB000000000K15/0SC/" + df4['id']
    df4['location__v'] = df4['location__v'].fillna(df4['country__v'])
    return pd.concat([df, df4], axis=0, ignore_index=True)


def getCountries(sessionId, df, url):
    headers = {'Authorization': sessionId}
    for country in df['country__v']:
        endpoint = url + "/vobjects/country__v/" + country
        response = requests.get(endpoint, headers=headers)
        df.loc[df['country__v'] == country, 'Country'] = response.json()['data']['name__v']
    return df


def polishDf(df):
    df = df.rename(columns={'state__v': 'State', 'name__v': 'StudyNumber', 'address_line_1__clin': 'Address',
                            'status__v': 'Status'})
    df = df.fillna('N/A')
    df['SizeDots'] = df['id'].apply(lambda id: idToSize(id))
    return df


def idToSize(input):
    if input.find('0SC') != -1:
        return 25
    else:
        return 10


def getMapInfo():
    with open('config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    base_api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version']
    sessionId = getSessionId(config, base_api_url)
    sites = getSites(sessionId, base_api_url)
    sitesAttributes = getSitesAttributes(sessionId, sites, config, base_api_url)
    siteCountries = getSiteCountries(sessionId, sitesAttributes, config, base_api_url)
    mapInfo = getLocations(sessionId, siteCountries, base_api_url)
    mapInfo = getCountries(sessionId, mapInfo, base_api_url)
    mapInfo = polishDf(mapInfo)
    return mapInfo

getMapInfo()
################## 1 SITES
# df = pd.DataFrame(response.json()['data'])

################## 2 SITES ATTRIBUTES
# df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'site_status__v'])
# for id in df['id']:
#     api_url = url + "/vobjects/site__v/" + id
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
# URL: https://candidate-tech-services---sergio.veevavault.com/ui/#t/0TB000000000K15/0ST/0SI000000002001
# 3 Iterar en locations para tener coordenadas
# 4 Montar DF
