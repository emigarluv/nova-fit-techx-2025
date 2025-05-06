

#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################
import random
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from google.cloud import bigquery
from advice_generator import generate_content
from image_generator import generate_motivational_image
from datetime import datetime

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}

project_id = "egarcia154techx25"
dataset_id = "ISE"

def get_user_sensor_data(user_id, workout_id):
    """Returns a list of timestampped information for a given workout."""
    client = bigquery.Client(project=project_id)
    
    # The correct way to use query parameters in BigQuery
    query = """
        SELECT SensorId, Timestamp, SensorValue
        FROM `{}.{}.SensorData`
        WHERE WorkoutID = @workout_id
        ORDER BY Timestamp ASC
    """.format(project_id, dataset_id)
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("workout_id", "STRING", workout_id)
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()
        
        # Convert to list of dictionaries
        sensor_data = []
        for row in rows:
            sensor_data.append({
                'sensor_type': row.SensorId,
                'timestamp': row.Timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'data': row.SensorValue
            })
        
        return sensor_data
    
    except Exception as e:
        print(f"Error querying BigQuery: {e}")
        return []  # Return empty list on error


def get_user_workouts(user_id):
    """Returns a list of workouts for the given user_id."""
    client = bigquery.Client(project=project_id)

    query = f"""
        SELECT
            WorkoutID as workout_id,
            UserId as user_id,
            StartTimestamp as start_timestamp,
            EndTimestamp as end_timestamp,
            StartLocationLat as start_lat,
            StartLocationLong as start_lng,
            EndLocationLat as end_lat,
            EndLocationLong as end_lng,
            TotalDistance as distance,
            TotalSteps as steps,
            CaloriesBurned as calories_burned
        FROM `{project_id}.{dataset_id}.Workouts`
        WHERE UserID = @user_id
        ORDER BY StartTimestamp DESC
        LIMIT 11
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()

        workouts = []
        for row in results:
            workouts.append({
                "workout_id": row.workout_id,
                "start_timestamp": str(row.start_timestamp),
                "end_timestamp": str(row.end_timestamp),
                "start_lat": row.start_lat,
                "start_lng": row.start_lng,
                "end_lat": row.end_lat,
                "end_lng": row.end_lng,
                "distance": row.distance,
                "steps": row.steps,
                "calories_burned": row.calories_burned,
            })
        return workouts

    except Exception as e:
        print(f"Error fetching workouts from BigQuery: {e}")
        return []



def get_user_profile(user_id):
    client = bigquery.Client()

    query = f"""
        SELECT Name, Username, DateOfBirth, ImageUrl, UserId
        FROM `egarcia154techx25.ISE.Users`
        WHERE UserId = @user_id
        LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    result = list(query_job.result())

    if not result:
        return None

    user = result[0]

    friends =  get_friends_list(user_id)

    return {
        "full_name": user["Name"],
        "username": user["Username"],
        "date_of_birth": user["DateOfBirth"],
        "profile_image": user["ImageUrl"],
        "friends": friends,
        'user_id': user['UserId']
    }

def get_friends_list(user_id):
    client = bigquery.Client()

    query = """
        SELECT
            CASE
                WHEN UserId1 = @user_id THEN UserId2
                ELSE UserId1
            END AS FriendUserId
        FROM `egarcia154techx25.ISE.Friends`
        WHERE UserId1 = @user_id OR UserId2 = @user_id
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    return [row["FriendUserId"] for row in results]


def get_user_posts(user_id):
    """Returns a list of a user's posts.
    """
    client = bigquery.Client()

    query = """
        SELECT PostId, AuthorId, Timestamp, Content, ImageUrl
        FROM `egarcia154techx25.ISE.Posts`
        WHERE AuthorId = @user_id
        ORDER BY Timestamp DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    posts = []
    for row in results:
        posts.append({
            "user_id": row["AuthorId"],
            "post_id": row["PostId"],
            "timestamp": row["Timestamp"],
            "content": row.get("Content"),  # May be None
            "image": row.get("ImageUrl")    # May be None
        })

    return posts

def get_genai_advice(user_id):
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    advice = generate_content(user_id)
    # image = random.choice([None, generate_motivational_image()])
    if random.choice([True, False]):
        image = generate_motivational_image()
    else:
        image = None
    
    if image:
        image = "data:image/png;base64," + image
    
    return {
        'advice_id': 'advice1',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'content': advice,
        'image': image,
    }
