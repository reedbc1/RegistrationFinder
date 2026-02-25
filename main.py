import os
import googlemaps
import logging
import requests
import pandas as pd
import json

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # load variables from .env into local environment
    from dotenv import load_dotenv
    load_dotenv()


def census_address(street: str, zip: str) -> tuple:
    """
    Get data from census geocoder API.
    Returns: (lng, lat, address, zip, city, state, county)
    """
    api_key: str = os.getenv("CENSUS_DATA_API_KEY")

    returntype: str = "geographies"
    searchtype: str = "address"

    url: str = f"https://geocoding.geo.census.gov/geocoder/{returntype}/{searchtype}?"

    params: dict = {
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

    data: dict = response.json()

    addressMatches: list = data.get("result", {}) \
                         .get("addressMatches", [])

    if addressMatches == []:
        raise Exception('Address not found.')

    address: str = addressMatches[0].get("matchedAddress")

    lng: float = addressMatches[0].get("coordinates", {}).get("x")
    lat: float = addressMatches[0].get("coordinates", {}).get("y")

    county_reg: str = (data.get("result",
                           {}).get("addressMatches",
                                   [])[0].get("geographies",
                                              {}).get("Counties",
                                                      [])[0].get("NAME"))

    county: str = ' '.join(list(map(str.capitalize, county_reg.split(' '))))

    try:
        city: str = address.split(',')[1].strip()
        state: str = address.split(',')[2].strip()
        zip: str = address.split(',')[3].strip()

    except (IndexError, AttributeError):
        city, state, zip = None, None, None

    return lng, lat, address, zip, city, state, county


def goog_geocode(address: str, zip: str) -> tuple:
    """
    Get data from Google Geocoder API.
    Returns: (lng, lat, formatted_address, zip, city, state)
    Note: Same returns as census_address, but doesn't return county.
    """
    print(os.environ)
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    """Temp. debugging code for github"""
    if api_key is not None:
        print(f"length of api key: {len(api_key)}")
    elif api_key is None:
        print(f"API key is None")
    else:
        print(f"API key is type: {type(api_key)}")

    gmaps = googlemaps.Client(key=api_key)

    try:
        data: list = gmaps.geocode(address + " " + zip)

    except Exception as e:
        logging.info("Google Geocoder API call was unsuccessful."
                     f"Error: {e}")
        raise e

    if len(data) == 0:
        raise Exception('Address not found.')

    elif len(data) > 1:
        logging.warning('Multiple addresses found, using the first one.')

    # extract the first result
    result: dict = data[0]

    # Extract the components
    components: list = result.get('address_components', [])

    # Find street number and route
    street_number: str | None = next(
        (c['long_name'] for c in components if 'street_number' in c['types']),
        None)
    route: str | None = next((c['long_name'] for c in components if 'route' in c['types']),
                 None)

    # Check if both exist, otherwise raise error.
    if not (street_number and route):
        logging.info("street_number and/or route not found.")
        raise Exception("Address not found.")

    # get longitude and latitude
    lng: float = result.get("geometry", {}).get("location", {}).get("lng")
    lat: float = result.get("geometry", {}).get("location", {}).get("lat")

    formatted_address: str = format_address(result.get("formatted_address"))

    # Extract postal code
    zip: None = None
    for component in components:
        if 'postal_code' in component.get('types', []):
            zip: str | None = component.get('long_name')
            break

    try:
        city: str = formatted_address.split(", ")[0]
    except IndexError:
        city: None = None

    state: None = None
    for component in components:
        if 'administrative_area_level_1' in component.get('types', []):
            state: str = component.get('short_name')
            break

    return lng, lat, formatted_address, zip, city, state


def format_address(address: str) -> str:
    """
    Formats address from google geocoder.
    Example input: 4444 Weber Rd, St. Louis, MO 63123, USA
    Example output: 4444 WEBER RD, ST LOUIS, MO 63123
    """

    return address.upper().strip().replace('.', '').replace("'", ' ').replace(
        ", USA", '')


def arcgis_county(lng: float, lat: float) -> str:
    """
    Returns county_name or raises Exception('Address not found.')
    Example output: St. Louis County
    """

    url: str = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Census_Counties/FeatureServer/0/query"

    params: dict = {
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
    data: dict = response.json()

    try:
        county_name: str = (
            data.get("features", [{}])[0]
                .get("attributes", {})
                .get("NAME")
        )
        return county_name

    except Exception as e:
        logging.error("County name not found by function: arcgis_county")
        logging.info(e)
        raise Exception("Address not found.")


def check_county(county: str) -> list[str, str] | None:
    """
    Check for status for counties other 
    than St. Louis County and Jefferson County
    Returns [geo_code, patron_type]
    """

    patron_types = pd.read_csv("csv_files/PatronTypes.csv")
    patron_types = patron_types[~patron_types["County"].isin(
        ['Saint Louis County', 'Jefferson County'])]

    try:
        result: list[str, str] = patron_types[patron_types["County"].str.lower(
        ) == county.lower()].loc[:, ["Geographic Code", "Patron Type"]]
        geo_code: str = result.iloc[0, 0]
        patron_type: str = result.iloc[0, 1]

    except IndexError:
        return None

    return [geo_code, patron_type]


def slc_libs(lng: float, lat: float, county: str) -> list[str, str, str] | None:
    """
    Checks for library district if county is St. Louis County.
    Otherwise, returns None.
    Returns: [geo_code, patron_type, library] | None
    """

    if county.lower() == "st. louis county":
        patron_types = pd.read_csv("csv_files/PatronTypes.csv")
        patron_types = patron_types[patron_types["County"] ==
                                    'Saint Louis County']
        patron_types = patron_types[["Geographic Code", "Patron Type"]]

        url: str = "https://services2.arcgis.com/w657bnjzrjguNyOy/ArcGIS/rest/services/AGS_Jurisdictions/FeatureServer/8/query"

        params: dict = {
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

        data: dict = response.json()

        library: str = (data.get("features",
                            [{}])[0].get("attributes",
                                         {}).get("LIBRARY_DISTRICT"))
        selected_row = patron_types[
            patron_types["Geographic Code"].str.lower() == library.lower()]
        geo_code: str = selected_row.iloc[0, 0]
        patron_type: str = selected_row.iloc[0, 1]

        library_format: list = list(map(str.capitalize, library.split(' ')))
        if library_format[0] == "St":
            library_format[0] = "St."

        library: str = ' '.join(library_format)

        return [geo_code, patron_type, library]

    else:
        return None


def jeffco_schools(lng: float, lat: float, county: str) -> str | None:
    """
    Checks for school district if county is Jefferson County.
    Otherwise, returns None.
    Returns school: str | None
    """

    if county.lower() == "jefferson county":

        url: str = "https://services1.arcgis.com/Ur3TPhgM56qvxaar/arcgis/rest/services/Tax_Districts/FeatureServer/0/query"

        params: dict = {
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

        data: dict = response.json()

        school: str = (data.get("features", [{}])[0].get("attributes",
                                                    {}).get("Name"))

        return school

    else:
        return None


class AddressDetails:
    """
    Define AddressDetails class for lookups.
    Store values to be displayed to user as class attributes for
    easy reference.
    """

    def __init__(self):
        attributes: list = [
            "address", "county", "library", "school", "geo_code", "patron_type"
        ]
        for attr in attributes:
            setattr(self, attr, None)

    def address_lookup(self, address: str, zip: str):
        """
        Determine patron code, geographic code, and other relevant information
        depending on location.
        """

        """
        Step 1:
        First, try Census Geocoder API. If it fails, try Google Geocoding API.
        Raise exception if details cannot be found from the address and zip.
        """
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

            self.county: str = arcgis_county(lng, lat)

        """
        Step 2:
        If address is in Washington, MO, return geo code (Washington Public Library)
        and patron type (Reciprocal)
        """
        if city.upper() == "WASHINGTON" and state.upper() == "MO":
            self.geo_code: str = "Washington Public Library"
            self.patron_type: str = "Reciprocal"
            return self.display_data()

        """
        Step 3:
        Check if address is in county (other than St. Louis County or Jefferson County)
        that has reciprocal or non-resident status. 
        If true, set geo code and patron type and return results.
        """
        lookup_county: list[str, str] | None = check_county(self.county)

        if lookup_county:
            self.geo_code: str = lookup_county[0]
            self.patron_type: str = lookup_county[1]
            return self.display_data()

        """
        Step: 4
        Check if address is in St. Louis County. 
        If true, set library, geo code, and patron type and return.
        """
        lookup_library: list[str, str, str] | None = slc_libs(lng, lat, self.county)

        if lookup_library:
            self.geo_code: str = lookup_library[0]
            self.patron_type: str = lookup_library[1]
            self.library: str = lookup_library[2]
            return self.display_data()

        """
        Step 5.
        Check if address is in Jefferson County.
        If true, set school, geo code, and patron type and return.
        """
        self.school: str | None = jeffco_schools(lng, lat, self.county)

        if self.school:

            self.geo_code = "Jefferson County"

            eligible_schools = ["northwest", "fox", "windsor"]
            if self.school.lower() in eligible_schools:
                self.patron_type: str = "Reciprocal"
            else:
                self.patron_type: str = "Non-Resident"

            return self.display_data()

        """
        Step 6.
        If address geo code and patron type has not yet been determined, 
        it is ineligible for a library card.
        """
        self.geo_code: str = "Ineligible"
        self.patron_type: str = "Ineligible"
        return self.display_data()

    def display_data(self) -> dict:
        """
        Called by self.address_lookup
        Returns relevant details for address depending on location:
        - address, county, geo_code, and patron type are always returned
        - library is returned if address is in St. Louis County
        - school is returned if address is in Jefferson County
        """
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

"""Local testing"""
if __name__ == "__main__":
    submission = AddressDetails()
    result: dict = submission.address_lookup("4444 Weber Rd.", "63123")
    print(json.dumps(result, indent=4))
