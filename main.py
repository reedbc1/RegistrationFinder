import requests
import json
import googlemaps
from datetime import datetime
import os
import pandas as pd


### functions for finding possible geo codes from ZIP code ###
# load patron types table
def load_patron_types_1():
    df = pd.read_csv('csv_files/PatronTypes.csv')
    df = df[df['County'] != 'Saint Louis County']
    df = df[df['County'] != 'Jefferson County']

    df = df.dropna()
    return df


def load_patron_types_2():
    df = pd.read_csv('csv_files/PatronTypes.csv')
    df = df[df['County'] == 'Saint Louis County']
    df = df.dropna()
    return df


# edit column names and process 'GEO CODE' column
def modify_df(df):
    new_list = []
    for item in list(df.columns):
        new_list.append(item.replace("\n", ""))

    new_list[3] = new_list[3][:11]
    df.columns = new_list

    df['GEO CODE'] = df['GEO CODE'].str.replace('\n', '', regex=False)
    df['GEO CODE'] = df['GEO CODE'].str.split('or')
    df['GEO CODE'] = df['GEO CODE'].apply(lambda lst: [w.strip() for w in lst])


# find possible geo codes
def find_geo_codes(df, zip):
    geo_codes = df.loc[df['ZIP CODE'] == zip, 'GEO CODE'].iloc[0]
    return geo_codes


### functions for USPS API ###
def get_token():
    payload = {
        "client_id": "cO2VbnmRHijlhai22yAAeVnoqoVBwnj4nwiIAlSUNJVPaMlC",
        "client_secret":
        "awV02jZVtPrHWg3jbiPOyBRxsS6HG7439JTS6f4QkuyACq3nNcGkSalum3SoPtL0",
        "grant_type": "client_credentials"
    }
    response = requests.post("https://apis.usps.com/oauth2/v3/token",
                             json=payload)

    return response


def validate_address(access_token, params):

    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + access_token
    }

    response = requests.get("https://apis.usps.com/addresses/v3/address",
                            headers=headers,
                            params=params)
    return response


def create_and_save_response(access_token, params):
    response = validate_address(access_token, params)
    with open('json_output/address_response.json', 'w') as f:
        json.dump(response.json(), f, indent=4)


def open_address_response():
    with open('json_output/address_response.json', 'r') as f:
        data = json.load(f)
        return data


def format_address(response):
    streetAddress = response['streetAddress']
    secondaryAddress = response['secondaryAddress']
    city = response['city']
    state = response['state']
    ZIPCode = response['ZIPCode']

    if secondaryAddress == '':
        pretty_address = streetAddress + '\n' + city + ', ' + state + ' ' + ZIPCode
        google_address = streetAddress + ', ' + city + ', ' + state + ' ' + ZIPCode
        stlcounty_address = streetAddress
    else:
        pretty_address = streetAddress + ' APT ' + secondaryAddress + '\n' + city + ', ' + state + ' ' + ZIPCode
        google_address = streetAddress + ' APT ' + secondaryAddress + ', ' + city + ', ' + state + ' ' + ZIPCode
        stlcounty_address = streetAddress + ' APT ' + secondaryAddress

    formatted_address = {
        'pretty_address': pretty_address,
        'google_address': google_address,
        'stlcounty_address': stlcounty_address
    }

    return formatted_address


### functions for Google Maps API ###
# Address is 'street, city, state'
def save_geocode_result(gmaps, address):

    geocode_result = gmaps.geocode(address)

    with open('json_output/geocode_result.json', 'w') as f:
        json.dump(geocode_result, f, indent=4)


def load_geocode_result():
    with open('json_output/geocode_result.json', 'r') as f:
        data = json.load(f)
        return data


def get_county(google_address):
    my_secret = os.environ['maps_api']
    gmaps = googlemaps.Client(key=my_secret)
    save_geocode_result(gmaps, google_address)
    result = load_geocode_result()
    result = result[0]['address_components']
    try:
        county = [
            item["long_name"] for item in result
            if "administrative_area_level_2" in item["types"]
        ][0]
        return county
    except IndexError:
        city = [
            item["long_name"] for item in result
            if item["long_name"] == "St. Louis"
        ][0]
        if city == "St. Louis":
            return "Saint Louis City"


### Functions for St. Louis County Maps ###
def address_slcl(address):
    # get address from USPS API

    ### Use address_points to get PARENT_LOC ###
    # maybe using querying would be faster than find
    BASE_URL = "https://maps.stlouisco.com/hosting/rest/services/Address_Points/MapServer/find"

    params = {
        "searchText": address,
        "searchFields": "FULL_ADDRESS",
        "layers": "0",
        "f": "json"
    }

    resp = requests.get(BASE_URL, params=params)
    data = resp.json()

    parent_loc = data['results'][0]['attributes']['PARENT_LOC']

    ### Use AGS_Parcels to get library code ###
    BASE_URL = "https://maps.stlouisco.com/hosting/rest/services/Maps/AGS_Parcels/MapServer/find"

    params = {
        "searchText": parent_loc,
        "searchFields": "PARENT_LOC",
        "layers": "0",
        "f": "json"
    }

    resp = requests.get(BASE_URL, params=params)
    data = resp.json()

    library_district = data['results'][0]['attributes']['LIBRARY_DISTRICT']

    return library_district


### Functions for JeffCo Maps
def check_jeffco_school(street_address):
    url = "https://services1.arcgis.com/Ur3TPhgM56qvxaar/ArcGIS/rest/services/Tax_Parcels/FeatureServer/2/query"

    params = {
        "where": f"Situs='{street_address}'",  # exact match, case-sensitive
        "outFields": "Situs, SchDesc",
        "f": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    school = data["features"][0]['attributes']['SchDesc']
    return school


# run all functions
def address_and_county(params):

    df = pd.read_csv(
        "csv_files/Loan Rule and Registration Cheat Sheets - ZIP Codes.csv")

    modify_df(df)

    # Find possible geo codes
    possible_codes = find_geo_codes(df, '63123')

    # Return code if only one code is possible
    if len(possible_codes) == 1:
        # need to return geo code and patron type
        return possible_codes[0]

    ### USPS API
    token = get_token()
    token = token.json()
    access_token = token["access_token"]

    # work on error handling here.
    create_and_save_response(access_token, params)
    response = open_address_response()
    response = response['address']

    # format address from response
    formatted_address = format_address(response)
    # pretty_address = formatted_address['pretty_address']

    # prepare address for google api
    google_address = formatted_address['google_address']

    # prepare address for st louis county maps api
    stlcounty_address = formatted_address['stlcounty_address']

    # initialize location variables
    street_address = response['streetAddress']
    city = response['city']
    state = response['state']
    county = get_county(google_address)

    # load patron types csv as df
    patron_types = load_patron_types_1()

    ### find geo_code and patron_type ###
    if city == "Washington" and state == "MO":
        return {
            "address": google_address,
            "geo_code": "Washington Public Library",
            "patron_type": "Reciprocal"
        }

    # find different way to find st louis city
    for location in patron_types['County']:
        if location == county:
            print("True!")
            select_row = patron_types[patron_types['County'] == county]
            geo_code = select_row['Geographic Code'].iloc[0]
            patron_type = select_row['Patron Type'].iloc[0]
            return {
                "geo_code": geo_code, 
                "patron_type": patron_type
            }

    if county == "St. Louis County":
        patron_types_stlc = load_patron_types_2()
        # filtered_df needs to have all lowercase geo codes
        library = address_slcl(stlcounty_address)
        library = library.lower()
        select_row = patron_types_stlc[patron_types_stlc['Geographic Code'].
                                       str.lower() == library.lower()]
        geo_code = select_row['Geographic Code'].iloc[0]
        patron_type = select_row['Patron Type'].iloc[0]
        return {
            "address": google_address,
            "geo_code": geo_code, 
            "patron_type": patron_type
        }

    elif county == "Jefferson County":
        # check school
        school = check_jeffco_school(street_address)
        valid_jeffco_schools = ['Fox', 'Northwest', 'Windsor']
        if school in valid_jeffco_schools:
            return {
                "address": google_address,
                "geo_code": "Jefferson County",
                "patron_type": "Reciprocal"
            }
        else:
            return {
                "address": google_address,
                "geo_code": "Jefferson County",
                "patron_type": "Non-Resident"
            }

    else:
        return {
            "address": google_address,
            "geo_code": "Ineligible", 
            "patron_type": "Ineligible"
        }


# tested city address successfully
# 7550 Lohmeyer Ave, Maplewood, MO 63143
# 6704 ARMISTEAD CT 63012
# 3301 ARMBRUSTER RD DE SOTO, MO 63020
params = {
    "streetAddress": "4214 summit knoll dr",
    "secondaryAddress": "",
    "city": "st louis",
    "state": "MO",
    "ZIPCode": "63129"
}

result = address_and_county(params)

print(result)

# def zip_and_geo_codes():
#     df = pd.read_csv(
#         "csv_files/Loan Rule and Registration Cheat Sheets - ZIP Codes.csv")

#     modify_df(df)

#     return df
