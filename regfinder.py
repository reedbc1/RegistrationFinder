import requests
import pandas as pd


### Loading patron types tables ###
# Does not contain St. Louis County or Jefferson County.
def load_patron_types_1():
    df = pd.read_csv("csv_files/PatronTypes.csv")
    df = df[~df["County"].isin(["Saint Louis County", "Jefferson County"])]
    return df.dropna()


# Contains St. Louis County only
def load_patron_types_2():
    df = pd.read_csv("csv_files/PatronTypes.csv")
    return df[df["County"] == "Saint Louis County"].dropna()


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


### Check zip code for only one option ###
def check_zip_code(zip_code, csv_path="csv_files/ZIPcodes.csv"):
    # Load and clean
    df = pd.read_csv(csv_path)

    # Clean column names
    cols = df.columns.str.replace("\n", "").str.lower().tolist()
    cols[3] = cols[3][:11]  # adjust 4th col
    df.columns = cols

    # Clean and split 'geo code' and 'patron type'
    for col in ["geo code", "patron type"]:
        df[col] = (df[col].str.replace("\n", "", regex=False).str.split(
            "or").apply(lambda lst: [w.strip() for w in lst]))
        # Keep only rows with exactly one value
        df = df[df[col].str.len() == 1]

    # Select relevant cols
    df = df[["zip code", "geo code", "patron type"]]

    # Lookup zip code
    filtered = df[df["zip code"] == int(zip_code)]
    if filtered.empty:
        return False

    geo, ptype = filtered.iloc[0, 1], filtered.iloc[0, 2]
    return [geo[0], ptype[0]]


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


### Functions for JeffCo Maps ###
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


### Main Function ###
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
            "address": address,
            "county": county,
            "geo_code": one_possibility[0],
            "patron_type": one_possibility[1]
        }

    # Check if patron is part of Washington Public Library
    if city.upper() == "WASHINGTON" and state == "MO":
        return {
            "address": address,
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
                    "address": address,
                    "county": county,
                    "geo_code": geo_code,
                    "patron_type": patron_type
                }
    except AttributeError:
        print('No county to compare!')

    # If county is St. Louis County, find library
    if county == "St. Louis County":
        patron_types_stlc = load_patron_types_2()
        library = " ".join(list(map(str.capitalize, address_slcl(street).split(' '))))
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


### Code to test ###
if __name__ == "__main__":
    street = "4444 weber rd"
    zip = "63123"
    result = address_lookup(street, zip)
    print(result)