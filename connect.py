import requests
import os
import time
import json
from dotenv import load_dotenv

load_dotenv()

def get_access_token(token_file = 'token_access.json'):

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('SECRET_ID')

    res = requests.post(
        url="https://www.warcraftlogs.com/oauth/token",
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret)
    )

    token_data = res.json()

    expires_at = time.time() + token_data["expires_in"]

    with open(token_file, "w") as f:
        json.dump({"access_token":token_data['access_token'], "expires_at": expires_at}, f) 

    return token_data['access_token']


def check_access_token(token_file = 'token_access.json'):

    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            cached = json.load(f)
        if time.time() < cached['expires_at']:
            return cached["access_token"]

    else:

        return False

def return_token():

    saved_token = check_access_token()
    if not saved_token:
        new_token = get_access_token()
        return new_token
    else:
        return saved_token