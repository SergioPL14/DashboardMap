import requests

vault_domain_name = "candidate-tech-services---sergio.veevavault.com"
version = "v22.1"
user = "sergio.pina@candidate.com"
pwd = "1MyPassword!"

api_url = "https://" + vault_domain_name + "/api/" + version + "/auth"

json_body = {'username': user, 'password': pwd}

response = requests.post(api_url, json_body)
print(response.json())
