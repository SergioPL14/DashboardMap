import json
import requests
import yaml
import pandas as pd

# Site -> Location + State -> Address (coordinates)

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/auth"

json_body = {'username': config['user'], 'password': config['pwd']}

response = requests.post(api_url, json_body)
print(response.json()['sessionId'])

headers = {'Authorization': response.json()['sessionId']}

api_url = "https://" + config['vault_domain_name'] + "/api/" + config['version'] + "/vobjects/location__v"
json_body = {'username': config['user'], 'password': config['pwd']}
response = requests.get(api_url, json_body, headers=headers)

print(response.json()['data'])
print(response.json()['data'][1]['id'])

for entry in response.json()['data']:
    df = df.append(entry['id'])

print(df)
