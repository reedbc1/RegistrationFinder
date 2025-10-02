from dotenv import load_dotenv
import os
import googlemaps
import logging
import requests
import pandas as pd

# load variables from .env into environment
load_dotenv()

def goog_geocode(address, zip):

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    gmaps = googlemaps.Client(key=api_key)

    data = gmaps.geocode(address + " " + zip)

    if len(data) == 0:
        raise Exception('Address not found.')
    
    elif len(data) > 1:
        logging.warning('Multiple addresses found, using the first one.')

    # extract the first result
    result = data[0]

    # get longitude and latitude
    lng = result.get("geometry", {}).get("location", {}).get("lng")
    lat = result.get("geometry", {}).get("location", {}).get("lat")

    formatted_address = format_address(result.get("formatted_address"))

    # Extract postal code
    zip = None
    for component in result.get('address_components', []):
        if 'postal_code' in component.get('types', []):
            zip = component.get('long_name')
            break

    city = None
    for component in result.get('address_components', []):
        if 'locality' in component.get('types', []):
            city = component.get('long_name')
            break

    state = None
    for component in result.get('address_components', []):
        if 'administrative_area_level_1' in component.get('types', []):
            state = component.get('short_name')
            break

    return lng, lat, formatted_address, zip, city, state

def format_address(address):
    # replace ST in county names with SAINT
    return address.upper().strip().replace('.', '').replace("'", ' ').replace(", USA", '')

def find_county(lng, lat):
    base_url = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/TIGERweb_Counties_v1/FeatureServer/0/query"

    params = {
        "where": "1=1",
        "geometryType": "esriGeometryPoint",
        "spatialRel": "esriSpatialRelIntersects",
        "geometry": f"{lng},{lat}",
        "inSR": "4326",
        "outFields": "NAME",
        "returnGeometry": "false",
        "f": "json"
    }

    # handle timeout errors and other request exceptions
    response = requests.get(base_url, params=params, timeout=5)
    data = response.json()
    county = data.get("features", [])[0].get("attributes", {}).get("NAME", None)

    # reintroduce after PatronTypes is standardized
    # replace ST in county names with SAINT
    # county = county.split(' ')
    # if county[0] == 'St.':
    #     county[0] = 'Saint'
    # county = ' '.join(county)

    return county

# check for only one result for zip code
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
        df[col] = df[col].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)

    # Select relevant cols
    df = df[["zip code", "geo code", "patron type"]]

    df.to_csv('exclusive_zips.csv')

    # Lookup zip code
    filtered = df[df["zip code"] == int(zip_code)]
    if filtered.empty:
        return None

    geo, ptype = filtered.iloc[0, 1], filtered.iloc[0, 2]
    return [geo, ptype]


# check for only one result for county
def check_county(county):
    patron_types = pd.read_csv("csv_files/PatronTypes.csv")
    patron_types = patron_types[~patron_types["County"].isin(['Saint Louis County', 'Jefferson County'])]

    try:
        result = patron_types[patron_types["County"].str.lower() == county.lower()].loc[:,["Geographic Code", "Patron Type"]]
        geo_code = result.iloc[0,0]
        patron_type = result.iloc[0,1]

    except IndexError:
        return None

    return [geo_code, patron_type]

def slc_libs(lng, lat, county):
    if county.lower() == "st. louis county":
        patron_types = pd.read_csv("csv_files/PatronTypes.csv")
        patron_types = patron_types[patron_types["County"] == 'Saint Louis County']
        patron_types = patron_types[["Geographic Code", "Patron Type"]]

        url = "https://services2.arcgis.com/w657bnjzrjguNyOy/ArcGIS/rest/services/AGS_Jurisdictions/FeatureServer/8/query"

        params = {
            "geometry": f"{lng},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "LIBRARY_DISTRICT",
            "returnGeometry": "false",
            "defaultSR": "4326",
            "f": "pjson"
        }

        # fix with better message for error handling
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()

        library = (
            data.get("features", [{}])[0]        # get first feature safely
                .get("attributes", {})           # get attributes dict
                .get("LIBRARY_DISTRICT")         # get LIBRARY_DISTRICT
            )
        selected_row = patron_types[patron_types["Geographic Code"].str.lower() == library.lower()]
        geo_code = selected_row.iloc[0,0]
        patron_type = selected_row.iloc[0,1]

        return [geo_code, patron_type, library]

    else:
        return None
    
def jeffco_schools(lng, lat, county):
    if county.lower() == "jefferson county":

        url = "https://services1.arcgis.com/Ur3TPhgM56qvxaar/arcgis/rest/services/Tax_Districts/FeatureServer/0/query"
        
        params = {
            "geometry": f"{lng},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "false",
            "defaultSR": "4326",
            "f": "pjson"
        }

        # fix with better message for error handling
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()

        school = (
            data.get("features", [{}])[0]
                .get("attributes", {})
                .get("Name")
            )
        
        return school
        
        
        # selected_row = patron_types[patron_types["Geographic Code"].str.lower() == library.lower()]
        # print(selected_row)
        # geo_code = selected_row.iloc[0,0]
        # patron_type = selected_row.iloc[0,1]

        # return [geo_code, patron_type, library]

    else:
        return None


def address_lookup(address, zip):
    lng, lat, address, zip, city, state = goog_geocode(address, zip)
    library = None

    county = find_county(lng, lat)
    print(county)

    ### Check for only one result based on zip code ###
    # is this necessary now?
    lookup_zip = check_zip_code(zip)

    if lookup_zip:
        if county == 'St. Louis County':
                library = 'St Louis County'
        else:
            library = None

        return {
            k: v
            for k, v in {
                "address": address,
                "county": county,
                "library": library,
                "geo_code": lookup_zip[0],
                "patron_type": lookup_zip[1]
            }.items() if v is not None
        }
    
    if city.upper() == "WASHINGTON" and state.upper() == "MO":
        return {
            "address": address,
            "geo_code": "Washington Public Library",
            "patron_type": "Reciprocal"
        }

    # standardize patrontypes table names - all saint instead of st
    lookup_county = check_county(county)

    if lookup_county:
        return {
            k: v
            for k, v in {
                "address": address,
                "county": county,
                "library": library,
                "geo_code": lookup_county[0],
                "patron_type": lookup_county[1]
            }.items() if v is not None
        }
    
    # if in st louis county, check library district
    lookup_library = slc_libs(lng, lat, county)

    if lookup_library:
        return {
            k: v
            for k, v in {
                "address": address,
                "county": county,
                "library": lookup_library[2],
                "geo_code": lookup_library[0],
                "patron_type": lookup_library[1]
            }.items() if v is not None
        }
    
    # if in jeffco, check school district
    lookup_school = jeffco_schools(lng, lat, county)

    if lookup_school:
        eligible_schools = ["northwest", "fox", "windsor"]
        if lookup_school in eligible_schools:
            return ...
        else:
            return ...

# 888 Main St, Herculaneum, MO 63048
result = address_lookup('888 Main St', '63048')
print(result)




# if in jefferson county, check for school district

# if still not found, return ineligible