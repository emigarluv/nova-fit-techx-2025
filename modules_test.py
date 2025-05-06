#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.

# python -m unittest modules_test.py
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts, validate_url, format_date, display_calories_row, display_map_row, display_miles_row, display_steps_row
import pandas as pd
from unittest.mock import patch
import streamlit as st
import data_fetcher
from unittest.mock import MagicMock, patch
import scipy.signal
from datetime import datetime

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function and its helpers."""
    
    def test_validate_url(self):
        """Test the validate_url function with various inputs"""
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://example.com/path/to/resource"))
        self.assertTrue(validate_url("https://subdomain.example.com/path?query=value"))
        
        self.assertFalse(validate_url("not_a_url"), "not_a_url has no protocol or domain")
        self.assertFalse(validate_url("ftp://example.com"), "ftp://example.com should not pass regex check") 
        self.assertFalse(validate_url("example.com"), "example.com does not have a protocol")  
    
    def test_format_date(self):
        """Test the format_date function with datetime objects"""
        self.assertEqual(
            format_date(datetime(2025, 3, 8, 14, 30)),
            "March 08, 2025 at 02:30 PM"
        )
        self.assertEqual(
            format_date(datetime(2024, 12, 25, 8, 15)),
            "December 25, 2024 at 08:15 AM"
        )
        self.assertEqual(
            format_date(datetime(2025, 1, 1, 0, 0)),
            "January 01, 2025 at 12:00 AM"
        )

        with self.assertRaises(AttributeError):  # datetime has no strftime if input is string
            format_date("03/08/2025")

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def setUp(self):
        """Set up test data for all the charts and data sets."""
        self.user_id = "user1"
        self.workouts_list = [
            {'workout_id': 'workout1', 'start_timestamp': '2024-01-01 00:00:00', 'end_timestamp': '2024-01-01 00:30:00',
             'start_lat': 1.1, 'start_lng': 4.1, 'end_lat': 1.2, 'end_lng': 4.2, 'distance': 2.5, 'steps': 3000, 'calories_burned': 250},
            {'workout_id': 'workout2', 'start_timestamp': '2024-01-01 01:00:00', 'end_timestamp': '2024-01-01 01:30:00',
             'start_lat': 1.3, 'start_lng': 4.3, 'end_lat': 1.4, 'end_lng': 4.4, 'distance': 3.0, 'steps': 3500, 'calories_burned': 300},
        ]
        self.sensor_data = [
            {'sensor_type': 'heart_rate', 'timestamp': '2024-01-01 00:01:00', 'data': 80},
            {'sensor_type': 'heart_rate', 'timestamp': '2024-01-01 00:02:00', 'data': 85},
            {'sensor_type': 'heart_rate', 'timestamp': '2024-01-01 00:03:00', 'data': 78},
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:04:00', 'data': 3},
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:02:00', 'data': 5},
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:03:00', 'data': 0.1},
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:03:00', 'data': 4},
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:02:00', 'data': 7}
        ]


    def test_display_miles_row(self):
        """Tests display_miles_row function."""
        with patch('streamlit.columns') as mock_columns:
                mock_col1, mock_col2 = MagicMock(), MagicMock()
                mock_columns.return_value = [mock_col1, mock_col2]
                mock_col1.__enter__.return_value = mock_col1
                mock_col2.__enter__.return_value = mock_col2

        with patch('streamlit.markdown'), patch('streamlit.line_chart') as mock_line_chart:
            display_miles_row(self.workouts_list)
            df = mock_line_chart.call_args[0][0]
            self.assertEqual(df['distance'].sum(), 5.5)
            self.assertEqual(df.index[0], '00:00:00')

    def test_display_calories_row(self):
        """Tests display_calories_row function."""
        with patch('streamlit.columns') as mock_columns:
                mock_col1, mock_col2 = MagicMock(), MagicMock()
                mock_columns.return_value = [mock_col1, mock_col2]
                mock_col1.__enter__.return_value = mock_col1
                mock_col2.__enter__.return_value = mock_col2

        with patch('streamlit.markdown'), patch('streamlit.line_chart') as mock_line_chart:
            display_calories_row(self.workouts_list)
            df = mock_line_chart.call_args[0][0]
            self.assertEqual(df['calories_burned'].sum(), 550)
            self.assertEqual(df.index[0], '00:00:00')
    
    def test_display_map_row(self):
        """Tests display_map_row function."""
        with patch('streamlit.columns') as mock_columns:
                mock_col1, mock_col2 = MagicMock(), MagicMock()
                mock_columns.return_value = [mock_col1, mock_col2]
                mock_col1.__enter__.return_value = mock_col1
                mock_col2.__enter__.return_value = mock_col2

        with patch('streamlit.markdown'), patch('streamlit.pydeck_chart') as mock_pydeck_chart:
            display_map_row(self.workouts_list)
            called_deck = mock_pydeck_chart.call_args[0][0]
            layers = called_deck.layers

            # Assertions for the first layer (workout 1)
            self.assertEqual(layers[0].data[0]['start'], [4.1, 1.1])
            self.assertEqual(layers[0].data[0]['end'], [4.2, 1.2])

            # Assertions for the second layer (workout 2)
            self.assertEqual(layers[1].data[0]['start'], [4.3, 1.3])
            self.assertEqual(layers[1].data[0]['end'], [4.4, 1.4])

    @patch('data_fetcher.get_user_sensor_data')
    @patch('streamlit.warning')
    def test_workout_summary_no_workouts(self, mock_warning, mock_get_user_sensor_data):
        """Tests display_activity_summary handling when no activity data exists."""
        mock_get_user_sensor_data.return_value = []
        display_activity_summary(self.user_id, None, self.sensor_data)
        mock_warning.assert_called_with("No activity found.")
    
    def test_missing_steps_key(self):
        # Simulate workouts with one missing 'steps'
        workouts_list = [
            {'steps': 1000, 'start_timestamp': '2023-01-01T08:00:00'},
            {'distance': 2.5, 'start_timestamp': '2023-01-01T09:00:00'}  # No 'steps' key here
        ]
        try:
            display_steps_row(workouts_list)
        except Exception as e:
            self.fail(f"display_steps_row raised an exception unexpectedly: {e}")

class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    @patch('streamlit.markdown')
    def test_display_genai_advice_valid_input(self, mock_markdown):
        """Test that st.markdown is called with expected HTML and values when given valid inputs."""
        content = 'Keep pushing forward!'
        image = 'https://example.com/image.jpg'

        display_genai_advice(content, image)

        mock_markdown.assert_called_once()
        html = mock_markdown.call_args[0][0]  

        self.assertIn(content, html)
        self.assertIn(image, html)
        self.assertIn("<div class='genai-advice-container'>", html)
        self.assertIn("<h1>", html)
        self.assertIn("</h1>", html)

    @patch('streamlit.markdown')
    def test_display_genai_advice_empty_content(self, mock_markdown):
        """Test that empty content still renders the h1 tag."""
        content = ''
        image = 'https://example.com/image.jpg'

        display_genai_advice(content, image)

        html = mock_markdown.call_args[0][0]
        self.assertIn('<h1></h1>', html)

    @patch('streamlit.markdown')
    def test_display_genai_advice_empty_image(self, mock_markdown):
        """Test that an empty image string still sets background-image URL properly."""
        content = 'Stay consistent!'
        image = ''

        display_genai_advice(content, image)

        html = mock_markdown.call_args[0][0]
        self.assertIn("url('')", html)

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_display_recent_workouts_handles_empty_list(self):
        """Tests if display_recent_workouts handles an empty list without crashing."""
        with patch("streamlit.warning") as mock_warning:
            display_recent_workouts([])
            mock_warning.assert_called_with("No recent workouts available.")

    def test_display_recent_workouts_happy_path(self):
        """Tests the happy path where valid workout data is displayed correctly."""
        workouts = [
            {
                "start_timestamp": "2024-01-01 06:30:00",
                "end_timestamp": "2024-01-01 07:00:00",
                "total_distance": 5.2,
                "total_steps": 6500,
                "calories_burned": 320
            },
            {
                "start_timestamp": "2024-01-01 19:00:00",
                "end_timestamp": "2024-01-01 19:45:00",
                "total_distance": 3.1,
                "total_steps": 4500,
                "calories_burned": 180
            }
        ]
        with patch("streamlit.dataframe") as mock_dataframe:
            display_recent_workouts(workouts)
            self.assertTrue(mock_dataframe.called, "Workout table should be displayed.")

    def test_display_recent_workouts_missing_keys(self):
        """Tests if display_recent_workouts shows an error for missing keys."""
        workouts = [
            {
                "start_timestamp": "2024-01-01 06:30:00",
                "end_timestamp": "2024-01-01 07:00:00",
                "total_distance": 5.2
                # Missing "total_steps" and "calories_burned"
            }
        ]
        with patch("streamlit.error") as mock_error:
            display_recent_workouts(workouts)
            mock_error.assert_called_with(f"Missing expected columns: {set(['calories_burned','total_steps'])}")


    def test_display_recent_workouts_progress_bar(self):
        """Tests if the progress bar correctly adjusts based on step count."""
        workouts = [
            {
                "start_timestamp": "2024-01-01 06:30:00",
                "end_timestamp": "2024-01-01 07:00:00",
                "total_distance": 5.2,
                "total_steps": 5000,  # Halfway to step goal
                "calories_burned": 320
            }
        ]
        with patch("streamlit.markdown") as mock_markdown:
            display_recent_workouts(workouts)
            self.assertTrue(mock_markdown.called, "Progress bar should be displayed.")

   
if __name__ == "__main__":
    unittest.main()
