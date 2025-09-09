import requests
import pandas as pd


# load patron types table. Does not contain St. Louis County or Jefferson County.
def load_patron_types_1():
    df = pd.read_csv('csv_files/PatronTypes.csv')
    df = df[df['County'] != 'Saint Louis County']
    df = df[df['County'] != 'Jefferson County']

    df = df.dropna()
    return df


# load patron types table for St. Louis County only
def load_patron_types_2():
    df = pd.read_csv('csv_files/PatronTypes.csv')
    df = df[df['County'] == 'Saint Louis County']
    df = df.dropna()
    return df


# edit column names and process 'geo code' column


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


def modify_zip_sheet(df):
    # clean up zip_sheet column names
    new_list = []
    for item in list(df.columns):
        new_list.append(item.replace("\n", ""))
    new_list[3] = new_list[3][:11]
    new_list = [item.lower() for item in new_list]
    df.columns = new_list

    # process 'geo code' column
    df['geo code'] = df['geo code'].str.replace('\n', '', regex=False)
    df['geo code'] = df['geo code'].str.split('or')
    df['geo code'] = df['geo code'].apply(lambda lst: [w.strip() for w in lst])

    # process 'patron type' column
    df['patron type'] = df['patron type'].str.split('or')
    df['patron type'] = df['patron type'].apply(
        lambda lst: [w.strip() for w in lst])

    # create counts of columns for filtering
    df['geo code count'] = [
        len(df['geo code'][i]) for i in range(len(df['geo code']))
    ]
    df['patron type count'] = [
        len(df['patron type'][i]) for i in range(len(df['patron type']))
    ]

    # filer to zip codes with only one possible geo code and patron type
    df = df[df['geo code count'] == 1]
    df = df[df['patron type count'] == 1]

    # select only the following columns
    df = df[['zip code', 'geo code', 'patron type']]

    # return dataframe
    return df


### See if there is only one possible geo. code ###
def check_zip_code(zip):
    # load zip code sheet
    zip_code_sheet = pd.read_csv("csv_files/ZIPcodes.csv")

    # format zip code sheet
    zip_code_sheet = modify_zip_sheet(zip_code_sheet)

    # check if zip code is found in zip_code sheet
    filtered_zip = zip_code_sheet[zip_code_sheet['zip code'] == int(zip)]
    
    if filtered_zip.empty:
        return False
    else:
        geo_and_type = [item[0] for item in filtered_zip.iloc[0].tolist()[1:3]]
        return geo_and_type

    
# run all functions
def address_lookup(street, zip):

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

    # Check if zip code has only one possible geo. code
    one_possibility = check_zip_code(zip)
    if one_possibility:
        return {
            "address": street,
            "county": county,
            "state": state,
            "geo_code": one_possibility[0],
            "patron_type": one_possibility[1]
        }
    
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


if __name__ == "__main__":
    result = address_lookup('4214 summit knoll dr', '63129')
    print(result)
