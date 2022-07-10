import requests
import yaml
import pandas as pd
from geopy.geocoders import Nominatim


def getHeaders(config, url):
    endpoint = url + "/auth"
    json_body = {'username': config['user'], 'password': config['pwd']}
    response = requests.post(endpoint, json_body)
    return {'Authorization': response.json()['sessionId']}


def getSites(headers, url):
    endpoint = url + "/vobjects/site__v"
    response = requests.get(endpoint, headers=headers)
    return pd.DataFrame(response.json()['data'])


def getSitesAttributes(headers, df, config, url):
    df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'site_status__v', 'country__v', 'url'])
    for id in df['id']:
        endpoint = url + "/vobjects/site__v/" + id
        response = requests.get(endpoint, headers=headers)
        df2 = pd.concat([df2, pd.DataFrame(response.json()['data'])[
            ['id', 'location__v', 'status__v', 'state__v', 'site_status__v', 'country__v']]], ignore_index=True)
    df2['url'] = "https://" + config['vault_domain_name'] + "/ui/#t/0TB000000000K15/0SI/" + df2['id']
    return pd.merge(df, df2, on="id")


def getLocations(headers, df, url):
    df2 = pd.DataFrame(columns=['id', 'address_line_1__clin', 'latitude', 'longitude'])
    geolocator = Nominatim(user_agent="dashboardmap")
    for loc in df['location__v']:
        try:
            endpoint = url + "/vobjects/location__v/" + loc
            response = requests.get(endpoint, headers=headers).json()['data']
            df_aux = pd.DataFrame(response)[["id", "address_line_1__clin"]]
            lat = geolocator.geocode(response['address_line_1__clin']).latitude
            lon = geolocator.geocode(response['address_line_1__clin']).longitude
        except Exception as e:
            endpoint = url + "/vobjects/country__v/" + loc
            response = requests.get(endpoint, headers=headers).json()['data']
            df_aux = pd.DataFrame(response)[["id"]]
            lat = geolocator.geocode(response['name__v']).latitude
            lon = geolocator.geocode(response['name__v']).longitude
        df_aux[["latitude", "longitude"]] = [lat, lon]
        df2 = pd.concat(
            [df2, df_aux], ignore_index=True)
    df2 = df2.rename(columns={'id': 'location__v'})
    return pd.merge(df, df2, on="location__v")


def getSiteCountries(headers, df, config, url):
    endpoint = url + "/vobjects/study_country__v"
    df_aux = pd.DataFrame(requests.get(endpoint, headers=headers).json()['data'])

    df2 = pd.DataFrame(columns=['id', 'location__v', 'status__v', 'state__v', 'country__v', 'url'])
    for id in df_aux['id']:
        endpoint = url + "/vobjects/study_country__v/" + id
        response = requests.get(endpoint, headers=headers)
        df2 = pd.concat([df2, pd.DataFrame(response.json()['data'])[
            ['id', 'status__v', 'state__v', 'country__v']]], ignore_index=True)
    df2['url'] = "https://" + config['vault_domain_name'] + "/ui/#t/0TB000000000K15/0SC/" + df2['id']
    df2['location__v'] = df2['location__v'].fillna(df2['country__v'])
    return pd.concat([df, df2], axis=0, ignore_index=True)


def getCountries(headers, df, url):
    for country in df['country__v']:
        endpoint = url + "/vobjects/country__v/" + country
        response = requests.get(endpoint, headers=headers)
        df.loc[df['country__v'] == country, 'Country'] = response.json()['data']['name__v']
    return df


def getColours(headers, df, url):
    endpoint = url + "/vobjects/colour_state__c"
    df_aux = pd.DataFrame(requests.get(endpoint, headers=headers).json()['data'])
    df2 = pd.DataFrame(columns=['id', 'colour__c', 'state__c'])
    for colour in df_aux['id']:
        endpoint = url + "/vobjects/colour_state__c/" + colour
        response = requests.get(endpoint, headers=headers)
        df2 = pd.concat([df2, pd.DataFrame(response.json()['data'])[
            ['id', 'colour__c', 'state__c']]], ignore_index=True)
    df2 = pd.merge(df_aux, df2, on="id")
    df2['colour__c'] = df2['colour__c'].str[:-3]
    df2['state__c'] = df2['state__c'].str.replace("__c", "__v")
    df2 = df2.drop(columns=['id', 'name__v'])
    df2 = df2.rename(columns={'state__c': 'state__v'})
    df = pd.merge(df, df2, on="state__v")
    return df


def polishDf(df):
    df = df.rename(columns={'state__v': 'State', 'name__v': 'StudyNumber', 'address_line_1__clin': 'Address',
                            'status__v': 'Status', 'colour__c': 'Colour'})
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
    headers = getHeaders(config, base_api_url)
    sites = getSites(headers, base_api_url)
    sitesAttributes = getSitesAttributes(headers, sites, config, base_api_url)
    siteCountries = getSiteCountries(headers, sitesAttributes, config, base_api_url)
    locations = getLocations(headers, siteCountries, base_api_url)
    countries = getCountries(headers, locations, base_api_url)
    colours = getColours(headers, countries, base_api_url)
    mapInfo = polishDf(colours)

    return mapInfo
