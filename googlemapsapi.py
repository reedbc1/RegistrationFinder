import googlemaps
from datetime import datetime
import os
import json

my_secret = os.environ['maps_api']

gmaps = googlemaps.Client(key=my_secret)


def save_result(address):
    # Address is 'street, city, state'
    geocode_result = gmaps.geocode(address)

    with open('json_output/geocode_result.json', 'w') as f:
        json.dump(geocode_result, f, indent=4)


def load_result():
    with open('json_output/geocode_result.json', 'r') as f:
        data = json.load(f)
        return data


save_result('1600 Amphitheatre Parkway, Mountain View, CA')
result = load_result()
result = result[0]['address_components']
county = [
    item["long_name"] for item in result
    if "administrative_area_level_2" in item["types"]
][0]
print(county)
