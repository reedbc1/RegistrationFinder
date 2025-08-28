import requests
import pandas as pd


### functions for finding possible geo codes from ZIP code ###
# load patron types table. Does not contain St. Louis County or Jefferson County.
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


# edit column names and process 'geo code' column
def modify_zip_sheet(df):
    new_list = []
    for item in list(df.columns):
        new_list.append(item.replace("\n", ""))
    new_list[3] = new_list[3][:11]
    new_list = [item.lower() for item in new_list]
    df.columns = new_list

    df['geo code'] = df['geo code'].str.replace('\n', '', regex=False)
    df['geo code'] = df['geo code'].str.split('or')
    df['geo code'] = df['geo code'].apply(lambda lst: [w.strip() for w in lst])


### Census API ###
def call_census_api(street, zip):

    returntype = "geographies"

    searchtype = "address"

    BASE_URL = f"https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}?"

    params = {
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "street": street,
        "zip": zip,
        "format": "json",
        # "layers": "all"
    }

    resp = requests.get(BASE_URL, params=params)
    data = resp.json()
    addressMatches = data.get("result", {}) \
                         .get("addressMatches", [])
    if addressMatches == []:
        raise Exception('Address not found.')
    return data


def get_matched_address(data):
    try:
        return data.get("result", {}) \
                   .get("addressMatches", [])[0] \
                   .get("matchedAddress")
    except (IndexError, AttributeError):
        return None


def get_county(data):
    try:
        return (data.get("result",
                         {}).get("addressMatches",
                                 [])[0].get("geographies",
                                            {}).get("Counties",
                                                    [])[0].get("NAME"))
    except (IndexError, AttributeError):
        return None


def get_street(data):
    try:
        address = get_matched_address(data)
        return address.split(',')[0].strip()
    except TypeError:
        return None


def get_city(data):
    try:
        address = get_matched_address(data)
        return address.split(',')[1].strip()
    except TypeError:
        return None


def get_state(data):
    try:
        address = get_matched_address(data)
        return address.split(',')[2].strip()
    except TypeError:
        return None


def get_zip(data):
    try:
        address = get_matched_address(data)
        return address.split(',')[3].strip()
    except TypeError:
        return None


### Functions for St. Louis County Maps ###
def address_slcl(address):

    ### Use address_points to get PARENT_LOC ###
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

    ### On AGS Parcels, use PARENT_LOC to get library code ###
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
def address_lookup(street, zip):

    # load zip code sheet (is this necessary now?)
    zip_code_sheet = pd.read_csv(
        "csv_files/Loan Rule and Registration Cheat Sheets - ZIP Codes.csv")

    # format zip code sheet
    modify_zip_sheet(zip_code_sheet)

    # call census api
    data = call_census_api(street, zip)

    # initialize location variables
    address = get_matched_address(data)
    street = get_street(data)
    city = get_city(data)
    state = get_state(data)
    zip = get_zip(data)
    county = get_county(data)

    # Doesn't include St Louis or Jefferson county
    patron_types = load_patron_types_1()

    # If zip code has only one match, return geo code and patron type
    # selected_row = zip_code_sheet[zip_code_sheet['zip code'] == zip]
    # if len(selected_row['geo code']) == 1:
    #     print()
    #     print('1 geo code')
    #     geo_code = selected_row['geo code'].iloc[0]
    #     patron_type = selected_row['patron type'].iloc[0]
    #     return {
    #         "address": address,
    #         "county": county,
    #         "geo_code": geo_code,
    #         "patron_type": patron_type
    #     }

    # Check if patron is part of Washington Public Library
    if city == "Washington" and state == "MO":
        return {
            "address": street,
            "city": city,
            "state": state,
            "geo_code": "Washington Public Library",
            "patron_type": "Reciprocal"
        }

    # Check for St Louis City and other counties
    try:
        for location in patron_types['County']:
            if location.lower() == county.lower():
                # patron_types is without st louis county
                select_row = patron_types[patron_types['County'].str.lower() ==
                                          location.lower()]
                geo_code = select_row['Geographic Code'].iloc[0]
                patron_type = select_row['Patron Type'].iloc[0]
                return {
                    "address": street,
                    "county": county,
                    "geo_code": geo_code,
                    "patron_type": patron_type
                }
    except AttributeError:
        print('No county to compare!')

    # If county is St. Louis County, find library
    if county == "St. Louis County":
        patron_types_stlc = load_patron_types_2()
        library = address_slcl(street)
        select_row = patron_types_stlc[patron_types_stlc['Geographic Code'].
                                       str.lower() == library.lower()]
        geo_code = select_row['Geographic Code'].iloc[0]
        patron_type = select_row['Patron Type'].iloc[0]
        return {
            "address": address,
            "county": county,
            "library": library,
            "geo_code": geo_code,
            "patron_type": patron_type
        }

    # If county is Jefferson County, find school district
    elif county == "Jefferson County":
        # check school
        school = check_jeffco_school(street)
        valid_jeffco_schools = ['Fox', 'Northwest', 'Windsor']
        if school in valid_jeffco_schools:
            return {
                "address": address,
                "county": county,
                "school_district": school,
                "geo_code": "Jefferson County",
                "patron_type": "Reciprocal"
            }
        else:
            return {
                "address": address,
                "county": county,
                "school_district": school,
                "geo_code": "Jefferson County",
                "patron_type": "Non-Resident"
            }

    else:
        return {
            "address": address,
            "state": state,
            "county": county,
            "geo_code": "Ineligible",
            "patron_type": "Ineligible"
        }


# 17419 Wildhorse Meadows Ln, Chesterfield, MO 63005
# result = address_lookup('4444 weber rd', '63123')
# print(result)
