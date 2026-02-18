from main import AddressDetails
import unittest

"""
Integration testing for the AddressLookup app.
Tests for all resident/reciprocal cases and verifies output.
"""

class TestMunicipal(unittest.TestCase):

    def test_brentwood(self):
        submission = AddressDetails()
        result = submission.address_lookup("1610 Oriole", "63144")
        test_case = {'address': '1610 ORIOLE LN, SAINT LOUIS, MO, 63144', 
                    'county': 'St. Louis County', 
                    'library': 'Brentwood', 
                    'geo_code': 'Brentwood', 
                    'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_fergusen(self):
        submission = AddressDetails()
        result = submission.address_lookup("9 S Hartnett Ave", "63135")
        test_case = {'address': '9 S HARTNETT AVE, SAINT LOUIS, MO, 63135', 
                     'county': 'St. Louis County', 
                     'library': 'Ferguson', 
                     'geo_code': 'Ferguson', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_kirkwood(self):
        submission = AddressDetails()
        result = submission.address_lookup("217 Peeke Ave", "63122")
        test_case = {'address': '217 PEEKE AVE, SAINT LOUIS, MO, 63122', 
                     'county': 'St. Louis County', 
                     'library': 'Kirkwood', 
                     'geo_code': 'Kirkwood', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_maplewood(self):
        submission = AddressDetails()
        result = submission.address_lookup("2521 Florent Ave", "63143")
        test_case = {'address': '2521 FLORENT AVE, SAINT LOUIS, MO, 63143', 
                     'county': 'St. Louis County', 
                     'library': 'Maplewood', 
                     'geo_code': 'Maplewood', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_richmond_heights(self):
        submission = AddressDetails()
        result = submission.address_lookup("7566 Warner Ave", "63117")
        test_case = {'address': '7566 WARNER AVE, SAINT LOUIS, MO, 63117', 
                     'county': 'St. Louis County', 
                     'library': 'Richmond Heights', 
                     'geo_code': 'Richmond Heights', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_rock_hill(self):
        submission = AddressDetails()
        result = submission.address_lookup("2908 Middlebush Ct", "63119")
        test_case = {'address': '2908 MIDDLEBUSH CT, SAINT LOUIS, MO, 63119', 
                     'county': 'St. Louis County', 
                     'library': 'Rock Hill', 
                     'geo_code': 'Rock Hill', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_university_city(self):
        submission = AddressDetails()
        result = submission.address_lookup("7561 Drexel Dr", "63130")
        test_case = {'address': '7561 DREXEL DR, SAINT LOUIS, MO, 63130', 
                     'county': 'St. Louis County', 
                     'library': 'University City', 
                     'geo_code': 'University City', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_valley_park(self):
        submission = AddressDetails()
        result = submission.address_lookup("529 Leonard Ave", "63088")
        test_case = {'address': '529 LEONARD AVE, VALLEY PARK, MO, 63088', 
                     'county': 'St. Louis County', 
                     'library': 'Valley Park', 
                     'geo_code': 'Valley Park', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_webster_groves(self):
        submission = AddressDetails()
        result = submission.address_lookup("206 S Elm Ave", "63119")
        test_case = {'address': '206 S ELM AVE, SAINT LOUIS, MO, 63119', 
                     'county': 'St. Louis County', 
                     'library': 'Webster Groves', 
                     'geo_code': 'Webster Groves', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

class TestStLouisCounty(unittest.TestCase):

    def test_st_louis_county(self):
        submission = AddressDetails()
        result = submission.address_lookup("4444 Weber Rd", "63123")
        test_case = {'address': '4444 WEBER RD, SAINT LOUIS, MO, 63123', 
                     'county': 'St. Louis County', 
                     'library': 'St. Louis County', 
                     'geo_code': 'St Louis County', 
                     'patron_type': 'Resident'}
        
        self.assertEqual(result, test_case)
    
class TestJeffersonCounty(unittest.TestCase):

    def test_fox(self):
        submission = AddressDetails()
        result = submission.address_lookup("2606 Seckman Rd", "63052")
        test_case = {'address': '2606 SECKMAN RD, IMPERIAL, MO, 63052', 
                     'county': 'Jefferson County', 
                     'school': 'Fox', 
                     'geo_code': 'Jefferson County', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_northwest(self):
        submission = AddressDetails()
        result = submission.address_lookup("6884 Providence Dr", "63051")
        test_case = {'address': '6884 PROVIDENCE DR, HOUSE SPRINGS, MO, 63051', 
                     'county': 'Jefferson County', 
                     'school': 'Northwest', 
                     'geo_code': 'Jefferson County', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_windsor(self):
        submission = AddressDetails()
        result = submission.address_lookup("1020 Palmer Ln", "63052")
        test_case = {'address': '1020 PALMER LN, IMPERIAL, MO, 63052', 
                     'county': 'Jefferson County', 
                     'school': 'Windsor', 
                     'geo_code': 'Jefferson County', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_other(self):
        submission = AddressDetails()
        result = submission.address_lookup("13022 Susan Dr", "63020")
        test_case = {'address': '13022 SUSAN DR, DE SOTO, MO, 63020', 
                     'county': 'Jefferson County', 
                     'school': 'DeSoto', 
                     'geo_code': 'Jefferson County', 
                     'patron_type': 'Non-Resident'}
        
        self.assertEqual(result, test_case)

class TestReciprocalCounty(unittest.TestCase):

    def test_st_louis_city(self):
        submission = AddressDetails()
        result = submission.address_lookup("2642 Michigan Ave", "63118")
        test_case = {'address': '2642 MICHIGAN AVE, SAINT LOUIS, MO, 63118', 
                     'county': 'St. Louis City', 
                     'geo_code': 'St Louis City', 
                     'patron_type': 'Reciprocal'}
        
        self.assertEqual(result, test_case)

    def test_warren(self):
        submission = AddressDetails()
        result = submission.address_lookup("112 E 1st St S", "63390")
        test_case = {
            "address": "112 E 1ST ST S, WRIGHT CITY, MO, 63390",
            "county": "Warren County",
            "geo_code": "Warren County",
            "patron_type": "Reciprocal"
        }
        
        self.assertEqual(result, test_case)

    def test_franklin(self):
        submission = AddressDetails()
        result = submission.address_lookup("116 Franklin Ave", "63084")
        test_case = {
            "address": "116 FRANKLIN AVE, UNION, MO, 63084",
            "county": "Franklin County",
            "geo_code": "Franklin County",
            "patron_type": "Reciprocal"
        }
        
        self.assertEqual(result, test_case)

    def test_gasconade(self):
        submission = AddressDetails()
        result = submission.address_lookup("411 S 5th St", "65066")
        test_case = {
            "address": "411 S 5TH ST, OWENSVILLE, MO, 65066",
            "county": "Gasconade County",
            "geo_code": "Gasconade County",
            "patron_type": "Reciprocal"
        }
        
        self.assertEqual(result, test_case)

    def test_st_charles(self):
        submission = AddressDetails()
        result = submission.address_lookup("2750 State Hwy K", "63368")
        test_case = {
            "address": "2750 STATE HWY K, O FALLON, MO, 63368",
            "county": "St. Charles County",
            "geo_code": "St Charles",
            "patron_type": "Reciprocal"
        }
        
        self.assertEqual(result, test_case)

class TestWashingtonMO(unittest.TestCase):

    def test_wash_mo(self):
        submission = AddressDetails()
        result = submission.address_lookup("405 E 7th St", "63090")
        test_case = {
            "address": "405 E 7TH ST, WASHINGTON, MO, 63090",
            "county": "Franklin County",
            "geo_code": "Washington Public Library",
            "patron_type": "Reciprocal"
        }
        
        self.assertEqual(result, test_case)


if __name__ == "__main__":
    unittest.main(verbosity=2)