#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
st.set_page_config(page_title="NovaFit", layout="wide")

from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts
from activity_page import display_activity_page,fetch_latest_posts
from community_page import display_community_page
from clubs_page import display_clubs_page
from nova_page import display_nova

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'


userId = 'user1'

def display_app_page():

    """Displays the home page of the app."""
    st.title('Welcome to NovaFit!')   
    # An example of displaying a custom component called "my_custom_component"
    # value = st.text_input('Enter your name')
    # display_my_custom_component(value)

     # --- TESTING `display_recent_workouts()` ---
    workouts = get_user_workouts(userId)  # Fetch workout data
    display_recent_workouts(workouts)  # Call your function

    profile = get_user_profile(userId)
    post = get_user_posts(userId)
    sensor_data = get_user_sensor_data(userId, workouts)
    display_post(profile['username'], profile['profile_image'], post[0]['timestamp'], post[0]['content'], post[0]['image'])
    display_activity_summary(userId, workouts, sensor_data)

    # --- TESTING `display_genai_advice` ---
    result = get_genai_advice('user3')
    content = result['content']
    image = result['image']
    display_genai_advice(content,image)
    
# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home","Community", "Activity", "Nova AI", "Clubs"])
    if page == "Home":
        display_app_page()
    elif page == "Activity":
        st.title("Activity Page")
        workouts_list = get_user_workouts(userId)
        latest_posts = fetch_latest_posts(limit=3)
        display_activity_page(userId,workouts_list,latest_posts)
    elif page == "Community":
        display_community_page(userId)
    elif page == 'Clubs':
        display_clubs_page()
    elif page == "Nova AI":
        display_nova()
        
