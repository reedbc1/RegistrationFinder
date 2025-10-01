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
    print(result)
    
    # get longitude and latitude
    lng = result.get("geometry", {}).get("location", {}).get("lng")
    lat = result.get("geometry", {}).get("location", {}).get("lat")

    # Extract postal code
    zip = None
    for component in result.get('address_components', []):
        if 'postal_code' in component.get('types', []):
            zip = component.get('long_name')
            break

    return lng, lat, format_address(result.get("formatted_address")), zip

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

    # replace ST in county names with SAINT
    county = county.split(' ')
    if county[0] == 'St.':
        county[0] = 'Saint'
    county = ' '.join(county)

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

    # Select relevant cols
    df = df[["zip code", "geo code", "patron type"]]

    # Lookup zip code
    filtered = df[df["zip code"] == int(zip_code)]
    if filtered.empty:
        return False

    geo, ptype = filtered.iloc[0, 1], filtered.iloc[0, 2]
    return [geo[0], ptype[0]]

def address_lookup(address, zip):
    lng, lat, address, zip = goog_geocode(address, zip)

    county = find_county(lng, lat)

    ### Check for only one result based on zip code ###
    one_possibility = check_zip_code(zip)

    if one_possibility:
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
                "geo_code": one_possibility[0],
                "patron_type": one_possibility[1]
            }.items() if v is not None
        }

print(address_lookup('4214 summit knoll dr', '63129'))

# check for only one result for county


# if in franklin county, check for washington, mo (city)

# if in st louis county, check for library district

# if in jefferson county, check for school district

# if still not found, return ineligible