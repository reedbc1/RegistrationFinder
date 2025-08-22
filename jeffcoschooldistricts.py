import requests

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

street_address = "6704 ARMISTEAD CT"
school = check_jeffco_school(street_address)
valid_jeffco_schools = ['Fox','Northwest','Windsor']
is_jeffco_recip = school in valid_jeffco_schools

print(school)
print(is_jeffco_recip)