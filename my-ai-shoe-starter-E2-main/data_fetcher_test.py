#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#
# python -m unittest data_fetcher_test.py
#############################################################################
import unittest
import pandas as pd
from datetime import datetime

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'

from data_fetcher import (
    get_user_sensor_data,
    get_user_workouts,
    get_user_profile,
    get_user_posts,
    get_genai_advice,
    get_friends_list,
    project_id,
    dataset_id,
)

from unittest.mock import MagicMock, patch
from google.cloud import bigquery


class TestDataFetcher(unittest.TestCase):
    @patch("data_fetcher.project_id", "test-project")
    @patch("data_fetcher.dataset_id", "test_dataset")
    def setUp(self):
        """Set up test data and mock database connection."""
        self.user_id = "user1"  # Changed to string to match data_fetcher.py
        self.workouts_list = [
            {
                "WorkoutID": "workout1",
                "start_timestamp": "2024-07-29 07:00:00",
                "end_timestamp": "2024-07-29 08:00:00",
                "start_lat_lng": (37.7749, -122.4194),
                "end_lat_lng": (37.8049, -122.421),
                "distance": 5.0,
                "steps": 8000,
                "calories_burned": 400.0,
            },
            {
                "WorkoutID": "workout2",
                "start_timestamp": "2024-07-29 09:00:00",
                "end_timestamp": "2024-07-29 10:00:00",
                "start_lat_lng": (40.7128, -74.006),
                "end_lat_lng": (40.7308, -73.9976),
                "distance": 6.5,
                "steps": 10000,
                "calories_burned": 500.0,
            },
        ]
        self.sensor_data = [
            {"sensor_type": "sensor1", "WorkoutID": "workout1", "timestamp": "2024-07-29 07:15:00", "data": 120.0},
            {"sensor_type": "sensor2", "WorkoutID": "workout1", "timestamp": "2024-07-29 07:30:00", "data": 3000.0},
            {"sensor_type": "sensor3", "WorkoutID": "workout1", "timestamp": "2024-07-29 07:45:00", "data": 36.5},
            {"sensor_type": "sensor1", "WorkoutID": "workout1", "timestamp": "2024-07-29 09:20:00", "data": 115.0},
            {"sensor_type": "sensor2", "WorkoutID": "workout1",  "timestamp": "2024-07-29 09:40:00", "data": 5000.0},
            {"sensor_type": "sensor3", "WorkoutID": "workout1", "timestamp": "2024-07-29 09:55:00", "data": 37.0},
        ]
        # Mock the database connection and cursor
        self.mock_client = MagicMock()
        self.mock_query_job = MagicMock()
        self.mock_client.query.return_value = self.mock_query_job
        self.patcher = patch("google.cloud.bigquery.Client", return_value=self.mock_client)
        self.patcher.start()

    def tearDown(self):
        """Clean up the mock database connection."""
        self.patcher.stop()
    
    def test_get_user_sensor_data(self):
        """Test get_user_sensor_data function."""
        # Mock the database query result
        mock_rows = [
            # Make sure these match the column names in your SQL query
            bigquery.Row(
                ("sensor1", pd.Timestamp("2024-07-29 07:15:00"), 120.0), 
                {"SensorId": 0, "Timestamp": 1, "SensorValue": 2}
            ),
            bigquery.Row(
                ("sensor2", pd.Timestamp("2024-07-29 07:30:00"), 3000.0), 
                {"SensorId": 0, "Timestamp": 1, "SensorValue": 2}
            ),
        ]          
        self.mock_query_job.result.return_value = mock_rows

        # Call the function
        workout_id = self.workouts_list[0]["WorkoutID"]
        result = get_user_sensor_data(self.user_id, workout_id)

        # Assertions
        self.mock_client.query.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["sensor_type"], "sensor1")
        self.assertEqual(result[0]["timestamp"], "2024-07-29 07:15:00")
        self.assertEqual(result[0]["data"], 120.0)
        self.assertEqual(result[1]["sensor_type"], "sensor2")
        self.assertEqual(result[1]["timestamp"], "2024-07-29 07:30:00")
        self.assertEqual(result[1]["data"], 3000.0)

    def test_get_user_sensor_data_no_data(self):
        """Test get_user_sensor_data function when no data is found."""
        # Mock the database query result to return an empty list
        self.mock_query_job.result.return_value = []

        # Call the function
        workout_id = self.workouts_list[0]["WorkoutID"]
        result = get_user_sensor_data(self.user_id, workout_id)

        # Assertions
        self.mock_client.query.assert_called_once()
        self.assertEqual(len(result), 0)
        
    @patch("data_fetcher.generate_content", return_value="Stay hydrated and keep moving!")
    @patch("data_fetcher.random.choice", return_value=None)
    def test_get_genai_advice_no_image(self, mock_random_choice, mock_generate_content):
        """Test get_genai_advice returns expected structure and mocked content."""
        result = get_genai_advice(self.user_id)

        
        mock_generate_content.assert_called_once_with(self.user_id)

        # Validate structure
        self.assertIn("advice_id", result)
        self.assertTrue(result["advice_id"].startswith("advice"))  
        self.assertIn("timestamp", result)
        self.assertIn("content", result)
        self.assertEqual(result["content"], "Stay hydrated and keep moving!")
        self.assertIn("image", result)
        self.assertIsNone(result["image"]) 
        
    @patch("data_fetcher.generate_content", return_value="Be proud of every small win!")
    @patch("data_fetcher.generate_motivational_image", return_value="https://example.com/test_image.jpg")
    @patch("data_fetcher.random.choice", return_value=True)
    def test_get_genai_advice_with_image(self, mock_random_choice, mock_generate_image, mock_generate_content):
        """Test get_genai_advice returns expected structure and mocked content."""
        result = get_genai_advice(self.user_id)

        mock_generate_content.assert_called_once_with(self.user_id)
        mock_generate_image.assert_called_once()

        self.assertIn("advice_id", result)
        self.assertTrue(result["advice_id"].startswith("advice"))  
        self.assertIn("timestamp", result)
        self.assertIn("content", result)
        self.assertEqual(result["content"], "Be proud of every small win!")
        self.assertIn("image", result)
        self.assertEqual(result["image"], "data:image/png;base64,https://example.com/test_image.jpg")


    def test_get_user_workouts_returns_list(self):
        """Test that get_user_workouts returns a list of workouts."""
        result = get_user_workouts(self.user_id)
        self.assertIsInstance(result, list)
    
    def test_get_user_workouts_structure(self):
        """Test that each workout has the expected keys."""
        result = get_user_workouts(self.user_id)
        if result:  # Only check structure if workouts exist
            keys = {"workout_id", "start_timestamp", "end_timestamp", "start_lat_lng",
                    "end_lat_lng", "distance", "steps", "calories_burned"}
            for workout in result:
                self.assertTrue(keys.issubset(workout.keys()))
    
    @patch("google.cloud.bigquery.Client")
    def test_get_user_workouts_bigquery_failure(self, mock_client_cls):
        """Test that get_user_workouts returns [] if BigQuery query fails."""
        mock_client = MagicMock()
        mock_client.query.side_effect = Exception("BigQuery error")
        mock_client_cls.return_value = mock_client

        result = get_user_workouts(self.user_id)
        self.assertEqual(result, [])


    @patch("google.cloud.bigquery.Client")
    def test_get_user_workouts_empty_result(self, mock_client_cls):
        """Test that an empty list is returned if user has no workouts."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        mock_client_cls.return_value = mock_client

        result = get_user_workouts(self.user_id)
        self.assertEqual(result, [])


    @patch("google.cloud.bigquery.Client")
    def test_get_user_workouts_query_format(self, mock_client_cls):
        """Test that BigQuery query is structured correctly."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        mock_client_cls.return_value = mock_client

        get_user_workouts(self.user_id)

        called_query = mock_client.query.call_args[0][0]
        self.assertIn("SELECT", called_query)
        self.assertIn("WorkoutID", called_query)
        self.assertIn("UserID = @user_id", called_query)

    
class TestGetUserProfile(unittest.TestCase):
    @patch('data_fetcher.get_friends_list', return_value=["user2", "user3"])
    @patch('data_fetcher.bigquery.Client')
    def test_get_user_profile(self, mock_bq_client, mock_get_friends):
        mock_user_result = MagicMock()
        mock_user_result.__iter__.return_value = iter([{
            "Name": "Alice Smith",
            "Username": "alice123",
            "DateOfBirth": datetime(1990, 1, 1),
            "ImageUrl": "https://example.com/alice.jpg",
            'UserId': 'user1'
        }])

        mock_bq_client.return_value.query.return_value.result.return_value = mock_user_result

        result = get_user_profile("user1")

        expected = {
            "full_name": "Alice Smith",
            "username": "alice123",
            "date_of_birth": datetime(1990, 1, 1),
            "profile_image": "https://example.com/alice.jpg",
            "friends": ["user2", "user3"],
            'user_id': 'user1'
        }

        self.assertEqual(result, expected)

class TestGetUserPosts(unittest.TestCase):

    @patch('data_fetcher.bigquery.Client')
    def test_get_user_posts(self, mock_bq_client):
        mock_post_result = MagicMock()
        mock_post_result.__iter__.return_value = iter([
            {
                "PostId": "post1",
                "AuthorId": "user1",
                "Timestamp": datetime(2023, 5, 1, 12, 0),
                "Content": "Hello world",
                "ImageUrl": "https://example.com/image1.jpg"
            },
            {
                "PostId": "post2",
                "AuthorId": "user1",
                "Timestamp": datetime(2023, 4, 20, 10, 0),
                "Content": None,
                "ImageUrl": None
            }
        ])

        mock_bq_client.return_value.query.return_value.result.return_value = mock_post_result

        result = get_user_posts("user1")

        expected = [
            {
                "user_id": "user1",
                "post_id": "post1",
                "timestamp": datetime(2023, 5, 1, 12, 0),
                "content": "Hello world",
                "image": "https://example.com/image1.jpg"
            },
            {
                "user_id": "user1",
                "post_id": "post2",
                "timestamp": datetime(2023, 4, 20, 10, 0),
                "content": None,
                "image": None
            }
        ]

        self.assertEqual(result, expected)

class TestGetFriendsList(unittest.TestCase):

    @patch('data_fetcher.bigquery.Client')
    def test_get_friends_list(self, mock_bq_client):
        mock_friend_result = MagicMock()
        mock_friend_result.__iter__.return_value = iter([
            {"FriendUserId": "user2"},
            {"FriendUserId": "user3"}
        ])

        mock_bq_client.return_value.query.return_value.result.return_value = mock_friend_result

        result = get_friends_list("user1")
        expected = ["user2", "user3"]

        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()