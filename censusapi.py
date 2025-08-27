import requests
import json

### Using U.S. Census Geocoder API ###

# replit does'nt have this package, but I can call the api with the requests package

# Test address:
# 3602 TRACEY RICH RD 1D St. Louis MO 63125

# Seems to be working! Let's use this instead of google maps api.
# Maybe it can replace the Jefferson County schools lookup,
# but I should probably use that since it is more likely to be up to date.

# I can possibly use the returned address for normalized address
# (Instead of USPS API)


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
  return data


# with open('json_output/census_geocode_result.json', 'w') as f:
#   json.dump(data, f, indent=4)


### Census API ###
def get_county_name(data):
  try:
    return (data.get("result", {}).get("addressMatches",
                                       [])[0].get("geographies",
                                                  {}).get("Counties",
                                                          [])[0].get("NAME"))
  except (IndexError, AttributeError):
    return None

def get_matched_address(data):
  try:
      return data.get("result", {}) \
                 .get("addressMatches", [])[0] \
                 .get("matchedAddress")
  except (IndexError, AttributeError):
      return None

def get_street(data):
  try:
      address = get_matched_address(data)
      return address.split(',')[0]
  except TypeError:
      return None

def get_city(data):
  try:
      address = get_matched_address(data)
      return address.split(',')[1]
  except TypeError:
      return None

def get_state(data):
  try:
      address = get_matched_address(data)
      return address.split(',')[2]
  except TypeError:
      return None

def get_zip(data):
  try:
      address = get_matched_address(data)
      return address.split(',')[3]
  except TypeError:
      return None


data = call_census_api('4214 summit knoll dr', '63129')

# Example usage
matched_address = get_matched_address(data)
print("Matched Address:", matched_address)



# Example usage
county_name = get_county_name(data)
print("County:", county_name)

street = get_street(data)
print("Street:", street)

test = None
print(test.lower())
