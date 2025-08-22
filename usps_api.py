import requests
import json


def get_token():
    payload = {
        "client_id": "cO2VbnmRHijlhai22yAAeVnoqoVBwnj4nwiIAlSUNJVPaMlC",
        "client_secret":
        "awV02jZVtPrHWg3jbiPOyBRxsS6HG7439JTS6f4QkuyACq3nNcGkSalum3SoPtL0",
        "grant_type": "client_credentials"
    }
    response = requests.post("https://apis.usps.com/oauth2/v3/token",
                             json=payload)

    with open("json_output/token.json", "w") as f:
        json.dump(response.json(), f, indent=4)
        # indent=4 makes it pretty-printed


def open_token():
    with open("json_output/token.json", "r") as f:
        data = json.load(f)
        return data


get_token()
token = open_token()
access_token = token["access_token"]


def validate_address(streetAddress, secondaryAddress, city, state, ZIPCode):
    params = {
        "streetAddress": streetAddress,
        "secondaryAddress": secondaryAddress,
        "city": city,
        "state": state,
        "ZIPCode": ZIPCode
    }

    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + access_token
    }

    response = requests.get("https://apis.usps.com/addresses/v3/address",
                            headers=headers,
                            params=params)
    return response


def create_and_save_response():
    response = validate_address("4444 weber road", "", "st louis", "MO",
                                "63123")
    with open('json_output/address_response.json', 'w') as f:
        json.dump(response.json(), f, indent=4)


def open_address_response():
    with open('json_output/address_response.json', 'r') as f:
        data = json.load(f)
        return data

create_and_save_response()
response = open_address_response()
print(response['address'])
