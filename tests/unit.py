import unittest
import sys
sys.path.append(r"C:\Users\reedb\Documents\Git Repos\RegistrationFinder") 
import main

from dotenv import load_dotenv
load_dotenv()

"""
Unit testing for the AddressLookup app.

Left off at check_county function in main.py
"""

class TestFunctions(unittest.TestCase):

    def test_census_address(self):
        result = main.census_address('4444 Weber Rd.', '63123')
        test_case = (
            -90.297902517867, 38.551378225846, 
            '4444 WEBER RD, SAINT LOUIS, MO, 63123', 
            '63123', 
            'SAINT LOUIS', 
            'MO', 
            'St. Louis County'
        )
        self.assertEqual(result, test_case)

    def test_goog_geocode(self):
        result = main.goog_geocode('4444 Weber Rd.', '63123')
        test_case = (
            -90.2980178, 38.5509335, 
            '4444 WEBER RD, ST LOUIS, MO 63123', 
            '63123', 
            '4444 WEBER RD', 
            'MO'
        )
        self.assertEqual(result, test_case)

    def test_format_address(self):
        result = main.format_address('4444 Weber Rd, St. Louis, MO 63123, USA')
        test_case = '4444 WEBER RD, ST LOUIS, MO 63123'
        self.assertEqual(result, test_case)
    
    def test_arcgis_county(self):
        lng = -90.29801780366506
        lat = 38.55106772021733
        result = main.arcgis_county(lng, lat)
        test_case = 'St. Louis County'
        self.assertEqual(result, test_case)


if __name__ == "__main__":
    unittest.main(verbosity=2)