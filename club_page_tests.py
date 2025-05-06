import unittest
from unittest.mock import patch, Mock
import requests
from clubs_page import find_places, get_place_details, get_photo_url

class TestClubLocatorBackend(unittest.TestCase):

    @patch('requests.get')
    def test_find_places_success(self, mock_get):
        mock_response = Mock()
        expected_data = {
            "results": [
                {"name": "Test Gym", "formatted_address": "123 Test St", "place_id": "abc123"}
            ]
        }
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        results = find_places("gym in Test City", "fake_api_key")
        self.assertEqual(results, expected_data["results"])

    @patch('requests.get')
    def test_find_places_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        results = find_places("gym in Test City", "fake_api_key")
        self.assertEqual(results, [])

    @patch('requests.get')
    def test_get_place_details_success(self, mock_get):
        mock_response = Mock()
        expected_data = {
            "result": {
                "opening_hours": {
                    "weekday_text": ["Monday: 9 AM – 5 PM"]
                }
            }
        }
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_get.return_value = mock_response

        result = get_place_details("abc123", "fake_api_key")
        self.assertEqual(result, expected_data["result"])

    @patch('requests.get')
    def test_get_place_details_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = get_place_details("abc123", "fake_api_key")
        self.assertEqual(result, {})

    def test_get_photo_url(self):
        photo_ref = "samplePhotoRef"
        api_key = "sampleKey"
        expected_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
        self.assertEqual(get_photo_url(photo_ref, api_key), expected_url)

if __name__ == '__main__':
    unittest.main()
