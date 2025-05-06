#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.

# terminal:
# streamlit run modules.py
#############################################################################

import streamlit as st
import pandas as pd

from internals import create_component
import streamlit as st

import numpy as np
import pandas as pd
import pydeck as pdk
from data_fetcher import get_user_workouts
from data_fetcher import get_user_sensor_data

import re
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from datetime import datetime
import requests

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'

#colors to choose from within color scheme
teal = (78, 160, 157)
mint = (184, 218, 195)
cream = (240, 238, 227)
orange = (231, 157, 98)
rust = (226, 102, 63)
dark_gray = (61, 62, 62)

# Function to convert RGB tuple to CSS rgb() string
def rgb_to_css(rgb):
    """
    Function to convert RGB tuple to CSS rgb() string
    
    Use the formatting > {rgb_to_css(teal)} < within an f string to use variables
    """
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    Args:
        value (str): The name you'd like to be called by within the app.
    """
    data = {'NAME': value}
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
     """Write a good docstring here."""
     pass
     """Displays user content and tracks its metadata.
     Returns: Nothing
     Creates a streamlit component that displays the passed inputs
     """
     default_img = 'https://images.ctfassets.net/7ajcefednbt4/4FRprjcsfoQjPaSyCIgxMz/d087162794d0452504f5be8226bd5e57/Lenny_Maughan.png'
     default_profile_img = 'https://pbs.twimg.com/profile_images/1120376586904199168/kOV0gNkL_400x400.jpg'

     if not is_valid_image_url(user_image):
        user_image = default_profile_img
        
     with st.container():
         col1, col2 = st.columns([1, 8])
 
         with col1:
             st.markdown(
                 f"""
                 <div style="display: flex; justify-content: center;">
                     <img src="{user_image}"style = "width: 75px;height: 75px; border-radius: 50%; object-fit: fit;"/>
                 </div>
                 """, unsafe_allow_html=True
             )
             
         with col2:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold;">{username}</span>                    
                </div>
                """, unsafe_allow_html=True
            )
            
            # Check if timestamp is a datetime object before formatting
            if isinstance(timestamp, datetime):
                st.caption(format_date(timestamp))
            else:
                st.caption(str(timestamp)) #or handle it differently
            st.write(content)
     
         if validate_url(post_image) and is_valid_image_url(post_image):
             st.image(post_image)
         else:
             st.image(default_img)
         
         st.markdown("---")

# --- display activity summary ---
# Used LLM to reformat into sepreate functions
def display_steps_row(workouts_list):
    """Displays the total steps and time graph of a user."""
    total_steps = sum(workout.get('steps', 0) for workout in workouts_list)
    steps_df = pd.DataFrame({
        'timestamp': [workout.get('start_timestamp') for workout in workouts_list],
        'steps': [workout.get('steps', 0) for workout in workouts_list]
    })
    steps_df = convert_timestamp_to_time(steps_df, 'timestamp')

    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f'<div class="centered-container"><span class="big-text">{total_steps}<br>Steps</span></div>', unsafe_allow_html=True)
    with col2:
        st.line_chart(steps_df.set_index('timestamp'), color=rgb_to_css(orange))

def display_miles_row(workouts_list):
    """Displays the total distance and time graph of a user."""
    total_distance = sum(workout['distance'] for workout in workouts_list)
    distance_df = pd.DataFrame({
        'timestamp': [workout['start_timestamp'] for workout in workouts_list],
        'distance': [workout['distance'] for workout in workouts_list]
    })
    distance_df = convert_timestamp_to_time(distance_df, 'timestamp')

    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f'<div class="centered-container"><span class="big-text">{total_distance:.3f}<br>Miles</span></div>', unsafe_allow_html=True)
    with col2:
        st.line_chart(distance_df.set_index('timestamp'), color=rgb_to_css(orange))

def display_calories_row(workouts_list):
    """Displays the total calories and time graph in the calories row"""
    total_calories = sum(workout['calories_burned'] for workout in workouts_list)
    calories_df = pd.DataFrame({
        'timestamp': [workout['start_timestamp'] for workout in workouts_list],
        'calories_burned': [workout['calories_burned'] for workout in workouts_list]
    })
    calories_df = convert_timestamp_to_time(calories_df, 'timestamp')

    st.markdown("<div class='centered-row'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f'<div class="centered-container"><span class="big-text">{total_calories}<br>Calories</span></div>', unsafe_allow_html=True)
    with col2:
        st.line_chart(calories_df.set_index('timestamp'), color=rgb_to_css(orange))

def display_map_row(workouts_list):
    """Displays the map of users workout start and end points."""
    st.markdown("""
    <style>
        .centered-map {
            display: flex;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)

    color_scheme = [teal, mint, cream, orange, rust, dark_gray]
    layers = []

    try:
        for i, workout in enumerate(workouts_list):
            start_lat = workout['start_lat'] # Access the separate values
            start_lon = workout['start_lng'] # Access the separate values
            end_lat = workout['end_lat'] # Access the separate values
            end_lon = workout['end_lng'] # Access the separate values
            color = color_scheme[i % len(color_scheme)]

            layer = pdk.Layer(
                "LineLayer",
                data=[{
                    'start': [start_lon, start_lat],
                    'end': [end_lon, end_lat],
                }],
                get_source_position="start",
                get_target_position="end",
                get_color=color,
                get_width=5,
                pickable=True
            )
            layers.append(layer)
    except (KeyError, ValueError, TypeError) as e:
        st.warning(f"Error processing map data: {e}")
        return

    st.markdown('<div class="centered-map">', unsafe_allow_html=True)
    st.pydeck_chart(pdk.Deck(layers=layers))
    st.markdown('</div>', unsafe_allow_html=True)

def display_activity_summary(user_id, workouts_list, sensor_data):
    """Main function to display the activity summary."""
    
    #st.set_page_config(page_title="Activity Summary", layout="wide")
    #st.markdown("<h1 style='text-align: left;'>WEBSITE TITLE</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; background-color: {rgb_to_css(orange)}; padding: 45px; border-radius: 5px; font-size: 72px;'>Today's Activity Summary</h2>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    .centered-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    .big-text {
        font-size: 4em;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    if not workouts_list:
        st.warning("No activity found.")
        return
    

    display_steps_row(workouts_list)
    display_miles_row(workouts_list)
    display_calories_row(workouts_list)
    #display_heart_rate_row(user_id, workouts_list, sensor_data)
    display_map_row(workouts_list)

def convert_timestamp_to_time(df, timestamp_column):
    df[timestamp_column] = pd.to_datetime(df[timestamp_column]).dt.strftime('%H:%M:%S')
    return df


def display_recent_workouts(workouts_list):
    """
    Displays a structured and visually enhanced summary of a user's recent workouts.

    Args:
        workouts_list (list): A list of dictionaries containing workout data.
    """

    if not workouts_list:
        st.warning("No recent workouts available.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(workouts_list)

    # Rename columns to match expected names
    df = df.rename(columns={
        "distance": "total_distance",
        "steps": "total_steps",
        "start_lat_lng": "start_coordinates",
        "end_lat_lng": "end_coordinates"
    })

    # Ensure expected columns exist
    expected_columns = {"start_timestamp", "end_timestamp", "total_distance", "total_steps", "calories_burned"}
    actual_columns = set(df.columns)

    if not expected_columns.issubset(actual_columns):
        st.error(f"Missing expected columns: {expected_columns - actual_columns}")
        return

    # Select relevant columns
    df = df[["start_timestamp", "end_timestamp", "total_distance", "total_steps", "calories_burned"]]

    # --- UI Styling ---
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;700&family=Nunito:wght@300;400;700&display=swap');

            body { background-color: #FCEFF9; font-family: 'Poppins', sans-serif; }
            
            .main-title { 
                text-align: center; 
                font-size: 42px; 
                font-weight: 700; 
                color: #FF6B6B; 
                margin-top: 30px; 
                font-family: 'Poppins', sans-serif;
                text-shadow: 2px 2px 4px rgba(255, 107, 107, 0.5);
            }
            
            .section-title { 
                font-size: 28px; 
                font-weight: bold; 
                color: #FF6B6B; 
                margin-top: 20px; 
                font-family: 'Poppins', sans-serif;
                text-shadow: 1px 1px 3px rgba(255, 107, 107, 0.5);
            }

            .stDataFrame { 
                background-color: #FFF5F7 !important; 
                border-radius: 12px; 
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5); 
            }

            .progress-container { margin-top: 10px; text-align: center; }

            .progress-bar { 
                width: 100%; 
                height: 18px; 
                background: #F4A261; 
                border-radius: 10px; 
                position: relative; 
            }
            
            .progress-fill { 
                height: 18px; 
                background: #E76F51; 
                border-radius: 10px; 
                position: absolute; 
                top: 0; 
                left: 0; 
            }

            .progress-indicator { 
                position: absolute; 
                top: -8px; 
                width: 20px; 
                height: 20px; 
                background: white; 
                border-radius: 50%; 
                border: 3px solid #E76F51; 
            }
            
            .success-box { 
                background-color: #A3E4DB; 
                border-radius: 10px; 
                padding: 12px; 
                text-align: center; 
                font-weight: bold; 
                color: #155724;
                margin-top: 10px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            }

            .metric-container { 
                background-color: #FFF5F7; 
                padding: 12px; 
                border-radius: 12px; 
                text-align: center; 
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            .metric-label {
                font-size: 18px;
                color: #6D6875;
                font-family: 'Nunito', sans-serif;
            }

            .metric-value {
                font-size: 26px;
                font-weight: bold;
                color: #FF8E9E;
                font-family: 'Nunito', sans-serif;
            }
            
        </style>
        """, unsafe_allow_html=True)

    # --- Page Title ---
    st.markdown("<h2 class='main-title'>🏃 Recent Workouts</h2>", unsafe_allow_html=True)

    # --- Display Workout Table ---
    st.markdown("<h3 class='section-title'>📝 Workout Summary</h3>", unsafe_allow_html=True)
    st.dataframe(df, width=700)

    # --- Calculate Total Stats ---
    total_steps = df["total_steps"].sum()
    total_distance = df["total_distance"].sum()
    total_calories = df["calories_burned"].sum()

    # --- Display Metrics with Icons ---
    st.markdown("<h3 class='section-title'>📊 Stats Overview</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.image("https://www.freeiconspng.com/uploads/walking-icon-29.png", width=60)
        st.markdown("<p class='metric-label'>🚶 Steps</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{total_steps:,}</p>", unsafe_allow_html=True)

    with col2:
        st.image("https://cdn-icons-png.freepik.com/512/7509/7509065.png", width=60)
        st.markdown("<p class='metric-label'>📏 Distance</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{total_distance:.2f} miles</p>", unsafe_allow_html=True)

    with col3:
        st.image("https://i.pinimg.com/564x/8f/a8/8a/8fa88ac13e6fa997130d46f565ceb10b.jpg", width=60)
        st.markdown("<p class='metric-label'>🔥 Calories</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{total_calories} kcal</p>", unsafe_allow_html=True)

    # --- Step Goal Progress Bar ---
    step_goal = 10000
    progress_percentage = min(1, total_steps / step_goal)
    progress_width = int(progress_percentage * 100)
    indicator_position = f"calc({progress_width}% - 10px)"

    st.markdown("<h3 class='section-title'>🎯 Daily Step Goal Progress</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_width}%;"></div>
            <div class="progress-indicator" style="left: {indicator_position};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # **Display Goal Achievement Message**
    if total_steps >= step_goal:
        st.markdown("<div class='success-box'>🎉 Congratulations! You've hit your step goal today! Keep going! 🚀</div>", unsafe_allow_html=True)


def display_genai_advice(content, image):
    """Displays an advice with an image background and a progress indicator.

    Parameters: 
        -content (str): The main text content displayed in the advice container. 
                        This is typically an advice or motivational quote.
                        
        -image (str): A URL pointing to the image used as the background.
        
        -time_progress (str): Text representing the progress of time.
    
     Returns:
        - None: This function does not return any value. 
    """
   
   #ChatGPT helped with the styling (CSS) and formatting to include the parameters into the markdown.
    st.markdown(
        f"""
<style>
    .genai-advice-container {{
        background-image: linear-gradient(rgba(61, 62, 62, 0.6), rgba(61, 62, 62, 0.6)),
        url('{image}');
        padding: 20px;
        border-radius: 8px;
        background-size: cover;
        background-position: center;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }}

    .genai-advice-container h1 {{
        color: #F0EEE3;
        font-weight: 1000;
        font-size: 3vw; 
        font-style: italic;
        padding: 1vh 2vw;
        white-space: normal; 
    }}
    
</style>
<div class='genai-advice-container'>
    <h1>{content}</h1>
</div>
""",
        unsafe_allow_html=True,
    )
    
def validate_url(url_string):
    '''Checks an input string and determines if it contains a valid url
    Returs: boolean True or False
    '''
    pattern = r'^(http|https)://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url_string):
        return False
    try:
        result = urlparse(url_string)
        if not all([result.scheme, result.netloc]):
            return False
        return True
    except:
        return False

def is_valid_image_url(url: str) -> bool:
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            return content_type.startswith("image/")
    except requests.RequestException:
        pass
    return False

def format_date(date):
    """Takes a datetime object and returns a string in the format 'Month DD, YYYY at HH:MM AM/PM'"""
    return date.strftime("%B %d, %Y at %I:%M %p")