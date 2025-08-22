import pandas as pd

df = pd.read_csv(
    "csv_files/Loan Rule and Registration Cheat Sheets - ZIP Codes.csv")


# edit column names and process 'GEO CODE' column
def modify_df():
  new_list = []
  for item in list(df.columns):
    new_list.append(item.replace("\n", ""))

  new_list[3] = new_list[3][:11]
  df.columns = new_list

  df['GEO CODE'] = df['GEO CODE'].str.replace('\n', '', regex=False)
  df['GEO CODE'] = df['GEO CODE'].str.split('or')
  df['GEO CODE'] = df['GEO CODE'].apply(lambda lst: [w.strip() for w in lst])


# find geo codes
def find_geo_codes(zip):
  geo_codes = df.loc[df['ZIP CODE'] == zip, 'GEO CODE'].iloc[0]
  return geo_codes


modify_df()

for code in df['GEO CODE']:
  print(code)

possible_codes = find_geo_codes('63123')

# def main():
#   ...
# if only one geo code in geo_result:
#   return geo_result[0]
# elif geo_result contains geo codes within St. louis county:
#   check county real estate tax
#   if not found:
#     check USPS
#   elif:
#     return correct geo code
#
# or check address first
# if county is st louis county, check real estate taxes
# if county is jefferson county, check schools site
# if county is other eligible county, return county in geo_result
# if zip code not found, return "Ineligible"
# use returned value to find patron type

# Start with USPS site to confirm address exists
#
