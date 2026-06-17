import sys
from pathlib import Path
import os
import unittest
import time

CWD = Path(os.getcwd())
sys.path.append(str(CWD))

from main import AddressDetails

from dotenv import load_dotenv
load_dotenv()

"""
Integration testing for the AddressLookup app.
Tests for all resident/reciprocal cases and verifies output.

Only primary important information is tested, including county, geo_code, 
and patron_code.

Specific addresses can be returned from different APIs and be slightly different,
which can trigger tests to fail. For this reason, they are not used in testing.

Future tests can be written to test non-resident and ineligible addresses.
"""

# defines parent class that waits 1 second after each test runs
class TestSleep(unittest.TestCase):
    def tearDown(self):
        time.sleep(1)

class TestMunicipal(TestSleep):

    def test_brentwood(self):
        submission = AddressDetails()
        result = submission.address_lookup("1610 Oriole", "63144")
        test_case = {'address': '1610 ORIOLE LN, SAINT LOUIS, MO, 63144', 
                    'county': 'St. Louis County', 
                    'library': 'Brentwood', 
                    'geo_code': 'Brentwood', 
                    'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_fergusen(self):
        submission = AddressDetails()
        result = submission.address_lookup("9 S Hartnett Ave", "63135")
        test_case = {'address': '9 S HARTNETT AVE, SAINT LOUIS, MO, 63135', 
                     'county': 'St. Louis County', 
                     'library': 'Ferguson', 
                     'geo_code': 'Ferguson', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])
        

    def test_kirkwood(self):
        submission = AddressDetails()
        result = submission.address_lookup("217 Peeke Ave", "63122")
        test_case = {'address': '217 PEEKE AVE, SAINT LOUIS, MO, 63122', 
                     'county': 'St. Louis County', 
                     'library': 'Kirkwood', 
                     'geo_code': 'Kirkwood', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_maplewood(self):
        submission = AddressDetails()
        result = submission.address_lookup("2521 Florent Ave", "63143")
        test_case = {'address': '2521 FLORENT AVE, SAINT LOUIS, MO, 63143', 
                     'county': 'St. Louis County', 
                     'library': 'Maplewood', 
                     'geo_code': 'Maplewood', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_richmond_heights(self):
        submission = AddressDetails()
        result = submission.address_lookup("7566 Warner Ave", "63117")
        test_case = {'address': '7566 WARNER AVE, SAINT LOUIS, MO, 63117', 
                     'county': 'St. Louis County', 
                     'library': 'Richmond Heights', 
                     'geo_code': 'Richmond Heights', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_rock_hill(self):
        submission = AddressDetails()
        result = submission.address_lookup("2908 Middlebush Ct", "63119")
        test_case = {'address': '2908 MIDDLEBUSH CT, SAINT LOUIS, MO, 63119', 
                     'county': 'St. Louis County', 
                     'library': 'Rock Hill', 
                     'geo_code': 'Rock Hill', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_university_city(self):
        submission = AddressDetails()
        result = submission.address_lookup("7561 Drexel Dr", "63130")
        test_case = {'address': '7561 DREXEL DR, SAINT LOUIS, MO, 63130', 
                     'county': 'St. Louis County', 
                     'library': 'University City', 
                     'geo_code': 'University City', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_valley_park(self):
        submission = AddressDetails()
        result = submission.address_lookup("529 Leonard Ave", "63088")
        test_case = {'address': '529 LEONARD AVE, VALLEY PARK, MO, 63088', 
                     'county': 'St. Louis County', 
                     'library': 'Valley Park', 
                     'geo_code': 'Valley Park', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_webster_groves(self):
        submission = AddressDetails()
        result = submission.address_lookup("206 S Elm Ave", "63119")
        test_case = {'address': '206 S ELM AVE, SAINT LOUIS, MO, 63119', 
                     'county': 'St. Louis County', 
                     'library': 'Webster Groves', 
                     'geo_code': 'Webster Groves', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

class TestStLouisCounty(TestSleep):

    def test_st_louis_county(self):
        submission = AddressDetails()
        result = submission.address_lookup("4444 Weber Rd", "63123")
        test_case = {'address': '4444 WEBER RD, SAINT LOUIS, MO, 63123', 
                     'county': 'St. Louis County', 
                     'library': 'St. Louis County', 
                     'geo_code': 'St Louis County', 
                     'patron_code': 'Resident'}
        
        for category in ['county', 'library', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])
    
class TestJeffersonCounty(TestSleep):

    def test_fox(self):
        submission = AddressDetails()
        result = submission.address_lookup("2606 Seckman Rd", "63052")
        test_case = {'address': '2606 SECKMAN RD, IMPERIAL, MO, 63052', 
                     'county': 'Jefferson County', 
                     'school': 'Fox', 
                     'geo_code': 'Jefferson County', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_northwest(self):
        submission = AddressDetails()
        result = submission.address_lookup("6884 Providence Dr", "63051")
        test_case = {'address': '6884 PROVIDENCE DR, HOUSE SPRINGS, MO, 63051', 
                     'county': 'Jefferson County', 
                     'school': 'Northwest', 
                     'geo_code': 'Jefferson County', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_windsor(self):
        submission = AddressDetails()
        result = submission.address_lookup("1020 Palmer Ln", "63052")
        test_case = {'address': '1020 PALMER LN, IMPERIAL, MO, 63052', 
                     'county': 'Jefferson County', 
                     'school': 'Windsor', 
                     'geo_code': 'Jefferson County', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_other(self):
        submission = AddressDetails()
        result = submission.address_lookup("13022 Susan Dr", "63020")
        test_case = {'address': '13022 SUSAN DR, DE SOTO, MO, 63020', 
                     'county': 'Jefferson County', 
                     'school': 'DeSoto', 
                     'geo_code': 'Jefferson County', 
                     'patron_code': 'Non-Resident'}
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

class TestReciprocalCounty(TestSleep):

    def test_st_louis_city(self):
        submission = AddressDetails()
        result = submission.address_lookup("2642 Michigan Ave", "63118")
        test_case = {'address': '2642 MICHIGAN AVE, SAINT LOUIS, MO, 63118', 
                     'county': 'St. Louis City', 
                     'geo_code': 'St Louis City', 
                     'patron_code': 'Reciprocal'}
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_warren(self):
        submission = AddressDetails()
        result = submission.address_lookup("112 E 1st St S", "63390")
        test_case = {
            "address": "112 E 1ST ST S, WRIGHT CITY, MO, 63390",
            "county": "Warren County",
            "geo_code": "Warren County",
            "patron_code": "Reciprocal"
        }
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_franklin(self):
        submission = AddressDetails()
        result = submission.address_lookup("116 Franklin Ave", "63084")
        test_case = {
            "address": "116 FRANKLIN AVE, UNION, MO, 63084",
            "county": "Franklin County",
            "geo_code": "Franklin County",
            "patron_code": "Reciprocal"
        }
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_gasconade(self):
        submission = AddressDetails()
        result = submission.address_lookup("411 S 5th St", "65066")
        test_case = {
            "address": "411 S 5TH ST, OWENSVILLE, MO, 65066",
            "county": "Gasconade County",
            "geo_code": "Gasconade County",
            "patron_code": "Reciprocal"
        }
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_st_charles(self):
        submission = AddressDetails()
        result = submission.address_lookup("2750 State Hwy K", "63368")
        test_case = {
            "address": "2750 STATE HWY K, O FALLON, MO, 63368",
            "county": "St. Charles County",
            "geo_code": "St Charles",
            "patron_code": "Reciprocal"
        }
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

class TestWashingtonMO(TestSleep):

    def test_wash_mo(self):
        submission = AddressDetails()
        result = submission.address_lookup("405 E 7th St", "63090")
        test_case = {
            "address": "405 E 7TH ST, WASHINGTON, MO, 63090",
            "county": "Franklin County",
            "geo_code": "Washington Public Library",
            "patron_code": "Reciprocal"
        }
        
        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

class TestNonresident(TestSleep):

    def test_bond(self):
        submission = AddressDetails()
        result = submission.address_lookup("518 E Main St", "62246")
        test_case = {
            "address": "518 E MAIN ST, GREENVILLE, IL 62246",
            "county": "Bond County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_calhoun(self):
        submission = AddressDetails()
        result = submission.address_lookup("201 Hanna Ave", "62006")
        test_case = {
            "address": "201 HANNA AVE, BATCHTOWN, IL 62006",
            "county": "Calhoun County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_clinton(self):
        submission = AddressDetails()
        result = submission.address_lookup("745 N 7th St", "62230")
        test_case = {
            "address": "745 N 7TH ST, BREESE, IL 62230",
            "county": "Clinton County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_jersey(self):
        submission = AddressDetails()
        result = submission.address_lookup("601 W Pine St", "62052")
        test_case = {
            "address": "601 W PINE ST, JERSEYVILLE, IL 62052",
            "county": "Jersey County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_macoupin(self):
        submission = AddressDetails()
        result = submission.address_lookup("711 N Charles St", "62626")
        test_case = {
            "address": "711 N CHARLES ST, CARLINVILLE, IL 62626",
            "county": "Macoupin County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_madison(self):
        submission = AddressDetails()
        result = submission.address_lookup("602 Hancock St", "62025")
        test_case = {
            "address": "602 HANCOCK ST, EDWARDSVILLE, IL 62025",
            "county": "Madison County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_monroe(self):
        submission = AddressDetails()
        result = submission.address_lookup("200 N Market St", "62298")
        test_case = {
            "address": "200 N MARKET ST, WATERLOO, IL 62298",
            "county": "Monroe County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_st_clair(self):
        submission = AddressDetails()
        result = submission.address_lookup("121 Timber Dr", "62226")
        test_case = {
            "address": "121 TIMBER DR, SWANSEA, IL 62226",
            "county": "St. Clair County",
            "geo_code": "Illinois",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

    def test_lincoln(self):
        submission = AddressDetails()
        result = submission.address_lookup("71 Nottingham Dr", "63379")
        test_case = {
            "address": "71 NOTTINGHAM DR, TROY, MO 63379",
            "county": "Lincoln County",
            "geo_code": "Other MO",
            "patron_code": "Non-Resident"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

class TestIneligible(TestSleep):
    
    def test_ineligible(self):
        submission = AddressDetails()
        result = submission.address_lookup("8015 Berry Ave", "32211")
        test_case = {
            "address": "8015 BERRY AVE, JACKSONVILLE, FL 32211",
            "county": "Duval County",
            "geo_code": "Ineligible",
            "patron_code": "Ineligible"
        }

        for category in ['county', 'geo_code', 'patron_code']:
            self.assertEqual(result[category], test_case[category])

if __name__ == "__main__":
    unittest.main(verbosity=2)