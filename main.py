import os
import googlemaps
import logging
import requests
import pandas as pd

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # load variables from .env into local environment
    from dotenv import load_dotenv
    load_dotenv()


def census_address(street, zip):
    api_key = os.getenv("CENSUS_DATA_API_KEY")

    returntype = "geographies"
    searchtype = "address"

    url = f"https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}?"

    params = {
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "street": street,
        "zip": zip,
        "format": "json",
        "key": api_key
    }

    response = requests.get(url, params=params, timeout=5)

    if response.status_code != requests.codes.ok:
        logging.info("Census API call was unsuccessful. " \
                     f"Response status code: {response.status_code}")
        response.raise_for_status()

    data = response.json()

    addressMatches = data.get("result", {}) \
                         .get("addressMatches", [])

    if addressMatches == []:
        raise Exception('Address not found.')

    address = addressMatches[0].get("matchedAddress")

    lng = addressMatches[0].get("coordinates", {}).get("x")
    lat = addressMatches[0].get("coordinates", {}).get("y")

    county_reg = (data.get("result",
                           {}).get("addressMatches",
                                   [])[0].get("geographies",
                                              {}).get("Counties",
                                                      [])[0].get("NAME"))

    county = ' '.join(list(map(str.capitalize, county_reg.split(' '))))

    try:
        city = address.split(',')[1].strip()
        state = address.split(',')[2].strip()
        zip = address.split(',')[3].strip()

    except (IndexError, AttributeError):
        city, state, zip = None, None, None

    return lng, lat, address, zip, city, state, county


# change code to use url and requests
# this will return json including "status"
# which will make issues more transparent
def goog_geocode(address, zip):

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    gmaps = googlemaps.Client(key=api_key)

    try:
        data = gmaps.geocode(address + " " + zip)

    except Exception as e:
        logging.info("Google Geocoder API call was unsuccessful."
                     f"Error: {e}")
        raise e

    if len(data) == 0:
        raise Exception('Address not found.')

    elif len(data) > 1:
        logging.warning('Multiple addresses found, using the first one.')

    # extract the first result
    result = data[0]

    # Extract the components
    # Use components for code down below, too
    components = result.get('address_components', [])

    # Find street number and route
    street_number = next(
        (c['long_name'] for c in components if 'street_number' in c['types']),
        None)
    route = next((c['long_name'] for c in components if 'route' in c['types']),
                 None)

    # Check if both exist, otherwise raise error.
    if not (street_number and route):
        raise Exception("Address not found.")

    # get longitude and latitude
    lng = result.get("geometry", {}).get("location", {}).get("lng")
    lat = result.get("geometry", {}).get("location", {}).get("lat")

    formatted_address = format_address(result.get("formatted_address"))

    # Extract postal code
    zip = None
    for component in components:
        if 'postal_code' in component.get('types', []):
            zip = component.get('long_name')
            break

    try:
        city = formatted_address.split(", ")[0]
    except IndexError:
        city = None

    state = None
    for component in components:
        if 'administrative_area_level_1' in component.get('types', []):
            state = component.get('short_name')
            break

    return lng, lat, formatted_address, zip, city, state


def format_address(address):
    return address.upper().strip().replace('.', '').replace("'", ' ').replace(
        ", USA", '')


def arcgis_county(lng, lat):
    url = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Census_Counties/FeatureServer/0/query"

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

    response = requests.get(url, params=params, timeout=5)
    data = response.json()

    try:
        county_name = (
            data.get("features", [{}])[0]
                .get("attributes", {})
                .get("NAME")
        )
        return county_name

    except Exception as e:
        print(e)
        raise Exception("Address not found.")

def check_zip(zip):

    df = pd.read_csv("csv_files/ExclusiveZips.csv")

    # Lookup zip code
    filtered = df[df["zip code"] == int(zip)].loc[:,
                                                  ["geo code", "patron type"]]
    if filtered.empty:
        return None

    geo_code, patron_type = filtered.iloc[0, 0], filtered.iloc[0, 1]
    return [geo_code, patron_type]


# check for only one result for county
def check_county(county):
    patron_types = pd.read_csv("csv_files/PatronTypes.csv")
    patron_types = patron_types[~patron_types["County"].isin(
        ['Saint Louis County', 'Jefferson County'])]

    try:
        result = patron_types[patron_types["County"].str.lower(
        ) == county.lower()].loc[:, ["Geographic Code", "Patron Type"]]
        geo_code = result.iloc[0, 0]
        patron_type = result.iloc[0, 1]

    except IndexError:
        return None

    return [geo_code, patron_type]


def slc_libs(lng, lat, county):

    if county.lower() == "st. louis county":
        patron_types = pd.read_csv("csv_files/PatronTypes.csv")
        patron_types = patron_types[patron_types["County"] ==
                                    'Saint Louis County']
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

        response = requests.get(url, params=params, timeout=5)

        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        data = response.json()

        # the problem
        library = (data.get("features",
                            [{}])[0].get("attributes",
                                         {}).get("LIBRARY_DISTRICT"))
        selected_row = patron_types[
            patron_types["Geographic Code"].str.lower() == library.lower()]
        geo_code = selected_row.iloc[0, 0]
        patron_type = selected_row.iloc[0, 1]

        library_format = list(map(str.capitalize, library.split(' ')))
        if library_format[0] == "St":
            library_format[0] = "St."

        library = ' '.join(library_format)

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

        response = requests.get(url, params=params, timeout=5)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()

        data = response.json()

        school = (data.get("features", [{}])[0].get("attributes",
                                                    {}).get("Name"))

        return school

    else:
        return None


class AddressDetails:

    def __init__(self):
        attributes = [
            "address", "county", "library", "school", "geo_code", "patron_type"
        ]
        for attr in attributes:
            setattr(self, attr, None)

    def address_lookup(self, address, zip):

        try:
            lng, lat, self.address, zip, city, state, self.county = census_address(
                address, zip)

            if None in [lng, lat, self.address, zip, city, state]:
                raise Exception(
                    "Census geocoder api failed to find all address details.")

        except Exception as e:
            logging.info(e)
            logging.info("Using Google Geocoder instead.")

            lng, lat, self.address, zip, city, state = goog_geocode(
                address, zip)
            if None in [lng, lat, self.address, zip, city, state]:
                raise Exception(
                    "Google geocoder failed to find all address details")

            self.county = arcgis_county(lng, lat)

        # if address is in Washington, MO, return details
        if city.upper() == "WASHINGTON" and state.upper() == "MO":
            self.geo_code = "Washington Public Library"
            self.patron_type = "Reciprocal"
            return self.display_data()

        # see if address is in county other than st. louis or jefferson
        lookup_county = check_county(self.county)

        if lookup_county:
            self.geo_code = lookup_county[0]
            self.patron_type = lookup_county[1]
            return self.display_data()

        # Check St. Louis County ArcGIS - library layer
        lookup_library = slc_libs(lng, lat, self.county)

        if lookup_library:
            self.geo_code = lookup_library[0]
            self.patron_type = lookup_library[1]
            self.library = lookup_library[2]
            return self.display_data()

        # Check Jefferson County ArcGIS - schools layer
        self.school = jeffco_schools(lng, lat, self.county)

        if self.school:

            self.geo_code = "Jefferson County"

            eligible_schools = ["northwest", "fox", "windsor"]
            if self.school.lower() in eligible_schools:
                self.patron_type = "Reciprocal"
            else:
                self.patron_type = "Non-Resident"

            return self.display_data()

        # If the address has made it this far, it's ineligible
        self.geo_code = "Ineligible"
        self.patron_type = "Ineligible"
        return self.display_data()

    def display_data(self):
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
    result = submission.address_lookup("1610 Oriole", "63144")
    print(result)
