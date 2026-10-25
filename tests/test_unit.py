import sys
import time
import unittest
from pathlib import Path
from unittest.mock import call, patch

import requests

# append current working directory to sys
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from dotenv import load_dotenv

import main

load_dotenv()

gmaps = main.get_gmaps_client()

"""
Unit testing for the AddressLookup app.
"""

class TestFunctions(unittest.TestCase):
    def tearDown(self):
        time.sleep(1)

    def test_goog_geocode(self):
        result = main.goog_geocode(gmaps, '4444 Weber Rd.', '63123')
        test_case = (
            -90.2980178, 38.5509335, 
            '4444 WEBER RD, ST LOUIS, MO 63123', 
            '63123', 
            'ST LOUIS', 
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

    def test_check_county(self):
        result = main.check_county('Warren County')
        test_case = ['Warren County', 'Reciprocal']
        self.assertEqual(result, test_case)

    def test_slc_libs(self):
        result = main.slc_libs(lng = -90.2980285287216, lat = 38.55093349998459, county = 'St. Louis County')
        test_case = ['St Louis County', 'Resident', 'St. Louis County']
        self.assertEqual(result, test_case)

    def test_jeffco_schools(self):
        result = main.jeffco_schools(lng = -90.5096530409488, lat = 38.311159280927086, county = 'Jefferson County')
        test_case = 'Fox'
        self.assertEqual(result, test_case)


class TestRetryDecorator(unittest.TestCase):
    @staticmethod
    def make_http_error(status_code):
        response = requests.Response()
        response.status_code = status_code
        response.url = "https://example.test/resource"
        return requests.exceptions.HTTPError(
            f"HTTP {status_code}",
            response=response,
        )

    def test_http_errors_with_retryable_status_codes_are_retried(self):
        with patch("main.time.sleep") as mock_sleep:
            for status_code in main.CODES_TO_RETRY:
                with self.subTest(status_code=status_code):
                    attempts = 0
                    error = self.make_http_error(status_code)

                    @main.retry(
                        max_attempts=2,
                        delay=1,
                        exceptions=(requests.exceptions.HTTPError,),
                    )
                    def succeeds_after_retry():
                        nonlocal attempts
                        attempts += 1
                        if attempts == 1:
                            raise error
                        return "success"

                    result = succeeds_after_retry()

                    self.assertEqual(result, "success")
                    self.assertEqual(attempts, 2)
                    mock_sleep.assert_called_once_with(1)
                    mock_sleep.reset_mock()

    def test_http_error_with_non_retryable_status_code_is_not_retried(self):
        attempts = 0
        error = self.make_http_error(404)

        @main.retry(
            max_attempts=3,
            delay=1,
            exceptions=(requests.exceptions.HTTPError,),
        )
        def always_fails():
            nonlocal attempts
            attempts += 1
            raise error

        with patch("main.time.sleep") as mock_sleep:
            with self.assertRaises(requests.exceptions.HTTPError) as context:
                always_fails()

        self.assertIs(context.exception, error)
        self.assertEqual(attempts, 1)
        mock_sleep.assert_not_called()

    def test_retryable_http_error_is_raised_after_attempts_are_exhausted(self):
        attempts = 0
        error = self.make_http_error(503)

        @main.retry(
            max_attempts=3,
            delay=1,
            backoff=2,
            exceptions=(requests.exceptions.HTTPError,),
        )
        def always_fails():
            nonlocal attempts
            attempts += 1
            raise error

        with patch("main.time.sleep") as mock_sleep:
            with self.assertRaises(requests.exceptions.HTTPError) as context:
                always_fails()

        self.assertIs(context.exception, error)
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_sleep.call_args_list, [call(1), call(2)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
