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
    url = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/TIGERweb_Counties_v1/FeatureServer/0/query"

    params = {
            "geometry": f"{lng},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "NAME",
            "returnGeometry": "false",
            "defaultSR": "4326",
            "f": "json"
        }
    

    # handle timeout errors and other request exceptions
    response = requests.get(url, params=params, timeout=5)
    data = response.json()
    county = data.get("features", [])[0].get("attributes", {}).get("NAME", None)

    return county


def check_zip(zip):
    df = pd.read_csv("csv_files\ExclusiveZips.csv")

    # Lookup zip code
    filtered = df[df["zip code"] == int(zip)]
    if filtered.empty:
        return None

    geo_code, patron_type = filtered.iloc[0, 1], filtered.iloc[0, 2]
    return [geo_code, patron_type]


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
            "f": "json"
        }

        # fix with better message for error handling
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()

        library = (
            data.get("features", [{}])[0]        
                .get("attributes", {})           
                .get("LIBRARY_DISTRICT")         
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
            "f": "json"
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

    else:
        return None
   
class AddressDetails:
    def __init__(self):
        attributes = ["address", "county", "library", "school", "geo_code", "patron_type"]
        for attr in attributes:
            setattr(self, attr, None)

    def address_lookup(self, address, zip):

        lng, lat, self.address, zip, city, state = goog_geocode(address, zip)

        self.county = find_county(lng, lat)

        lookup_zip = check_zip(zip)

        if lookup_zip:
            self.geo_code = lookup_zip[0]
            self.patron_type = lookup_zip[1]
            if self.county == 'St. Louis County':
                    library = 'St Louis County'
            return self.display_data()
        
        if city.upper() == "WASHINGTON" and state.upper() == "MO":
            self.geo_code = "Washington Public Library"
            self.patron_type = "Reciprocal"
            return self.diplay_data()

        # standardize patrontypes table names - all saint instead of st
        lookup_county = check_county(self.county)

        if lookup_county:
            self.geo_code = lookup_county[0]
            self.patron_type = lookup_county[1]
            return self.display_data()
        
        # if in st louis county, check library district
        lookup_library = slc_libs(lng, lat, self.county)

        if lookup_library:
            self.geo_code = lookup_library[0]
            self.patron_type = lookup_library[1]
            self.library = lookup_library[2]
            return self.diplay_data()
        
        # if in jeffco, check school district
        self.school = jeffco_schools(lng, lat, self.county)

        if self.school:

            self.patron_type = "Reciprocal"

            eligible_schools = ["northwest", "fox", "windsor"]
            if self.school.lower() in eligible_schools:
                self.geo_code = "Reciprocal"
            else:
                self.geo_code = "Non-Resident"
            
            return self.diplay_data()
        
        self.geo_code = "Ineligible"
        self.patron_type = "Ineligible"
        return self.display_data()
    
    def diplay_data(self):
        return {
            k: v
            for k, v in {
                "address": self.address,
                "county": self.county,
                "library": self.library,
                "school": self.school,
                "geo_code": self.geo_code,
                "patron_type": self.patron_type
            }.items() if v is not None
        }  

if __name__ == "__main__":
    submission = AddressDetails()
    result = submission.address_lookup("4444 weber rd", "63123")
    print(result)





