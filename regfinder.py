import requests
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


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
        "format": "json"
    }

    resp = requests.get(BASE_URL, params=params, timeout=5)
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


def split_address(address):
    try:
        street = address.split(',')[0].strip()
        city = address.split(',')[1].strip()
        state = address.split(',')[2].strip()
        zip = address.split(',')[3].strip()
        return street, city, state, zip
    except (IndexError, AttributeError):
        return None, None, None, None


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
    BASE_URL = "https://services2.arcgis.com/w657bnjzrjguNyOy/ArcGIS/rest/services/Address_Points/FeatureServer/2/query"

    params = {
        "where": f"PROP_ADD = '{address}'",
        "outFields": "PROP_ADD, PARENT_LOC",
        "f": "pjson"
    }

    resp = requests.get(BASE_URL, params=params, timeout=5)

    if resp.status_code == 200:
        data = resp.json()
    else:
        logging.info(f"Error: {resp.status_code}")
        raise Exception('Address not found.')

    parent_loc = data['features'][0]['attributes']['PARENT_LOC']

    # logging for debugging
    if len(data['features']) > 1:
        logging.info(
            "Warning: More than one address returned for Address_Points API. Might be apartments."
        )
        logging.info(f"{len(data['features'])} feature sets found.")

    ### On AGS Parcels, use PARENT_LOC to get library code ###
    BASE_URL = "https://services2.arcgis.com/w657bnjzrjguNyOy/ArcGIS/rest/services/Property_Built_by_Year/FeatureServer/0/query"

    params = {
        #where=PARENT_LOC+%3D+'26H531423'
        "where": f"PARENT_LOC = '{parent_loc}'",
        "outFields": "PROP_ADD, LIBRARY_DISTRICT",
        "f": "pjson"
    }

    resp = requests.get(BASE_URL, params=params)
    data = resp.json()

    library_district = data["features"][0]["attributes"]["LIBRARY_DISTRICT"]

    # logging for debugging
    if len(data['features']) > 1:
        logging.info(
            "Warning: More than one address returned for Property_Built_by_Year API. Results should be unique."
        )
        logging.info(f"{len(data['features'])} feature sets found.")

    library_district = " ".join(
        list(map(str.capitalize,
                 library_district.split(' '))))

    return library_district


### Functions for JeffCo Maps ###
def check_jeffco_school(street_address):
    url = "https://services1.arcgis.com/Ur3TPhgM56qvxaar/ArcGIS/rest/services/Tax_Parcels/FeatureServer/2/query"

    # this only really needs to be done in the beginning with the census api call.
    safe_address = street_address.replace("'", "''")  # escape single quotes

    params = {
        "where": f"Situs='{safe_address}'",  # exact match, case-sensitive
        "outFields": "Situs, SchDesc",
        "f": "pjson"
    }

    response = requests.get(url, params=params, timeout=5)
    data = response.json()

    school = data["features"][0]['attributes']['SchDesc']
    return school


### Main Function ###
def address_lookup(street, zip):

    # call census api
    data = call_census_api(street, zip)

    # initialize location variables
    address = get_matched_address(data)
    county = get_county(data)
    street, city, state, zip = split_address(address)
    if not all([address, county, street, city, state, zip]):
        raise Exception('Address not found.')

    # Doesn't include St Louis or Jefferson county
    patron_types = load_patron_types_1()

    # Check if zip code has only one possible geo. code
    one_possibility = check_zip_code(zip)
    
    if one_possibility:
        if county == 'St. Louis County':
            library = 'St Louis County'
        else:
            library = None
        
        return {
            k: v for k, v in {
                "address": address,
                "county": county,
                "library": library,
                "geo_code": one_possibility[0],
                "patron_type": one_possibility[1]
            }.items() if v is not None
        }

    # Check if patron is part of Washington Public Library
    if city.upper() == "WASHINGTON" and state.upper() == "MO":
        return {
            "address": address,
            "geo_code": "Washington Public Library",
            "patron_type": "Reciprocal"
        }

    # Check for St Louis City and other counties
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


### Code for local testing ###
if __name__ == "__main__":
    street = "244 US HWY 50"
    zip = "63091"
    result = address_lookup(street, zip)
    print(result)
