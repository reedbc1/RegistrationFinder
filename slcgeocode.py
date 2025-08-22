import requests

def address_slcl():
    # get address from USPS API
    address = "4214 SUMMIT KNOLL DR APT J"
    
    ### Use address_points to get PARENT_LOC ###
    # maybe using querying would be faster than find
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
    
    ### Use AGS_Parcels to get library code ###
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

print(address_slcl())