import requests
from getpass import getpass

BASE_URL = "http://localhost:81"
username = input('Username: ')
password = getpass('Password: ')

token_url = f"{BASE_URL}/api/token/"

resp = requests.post(token_url, data={"username": username, "password": password})
if resp.status_code == 200 and 'token' in resp.json():
    print(f"Your Paperless NGX API token is: {resp.json()['token']}")
else:
    print(f"Failed to obtain token! Status: {resp.status_code}")
    print(resp.text) 