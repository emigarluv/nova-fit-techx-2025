import streamlit as st
import requests
from PIL import Image

# Load environment variables from .env
API_KEY = 'AIzaSyAdjcCuxE3ytF2lOEpsMGxzt0X6a8EiqG0'

# Google Places API URLs
PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
PHOTO_URL = "https://maps.googleapis.com/maps/api/place/photo"

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding-top: 0rem;
    }
    .club-logo {
        border-radius: 5px;
    }
    .stExpander {
        border: 1px solid #ddd !important;
        border-radius: 5px !important;
        margin-bottom: 10px !important;
        background-color: black !important;
        color: white !important;
    }
    .stButton button {
        border-radius: 20px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .header {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
        color: white !important;
    }
    .location-display {
        text-align: center;
        margin-bottom: 20px;
        color: #ffffff;
        font-size: 18px;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 16px !important;
        color: #0066cc !important;
    }
    .search-container {
        display: flex;
        justify-content: center;
        max-width: 500px;
        margin: 0 auto;
        margin-bottom: 20px;
    }
    /* Set background color for containers */
    .stContainer {
        background-color: black !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to fetch places based on query
def find_places(query, api_key):
    params = {
        'query': query,
        'key': api_key
    }
    response = requests.get(PLACES_SEARCH_URL, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        st.error("Failed to fetch data from Google Places API")
        return []

# Function to fetch place details (e.g., hours)
def get_place_details(place_id, api_key):
    params = {
        'place_id': place_id,
        'fields': 'opening_hours',
        'key': api_key
    }
    response = requests.get(PLACE_DETAILS_URL, params=params)
    if response.status_code == 200:
        return response.json().get("result", {})
    return {}

# Function to construct the photo URL for places
def get_photo_url(photo_reference, api_key):
    return f"{PHOTO_URL}?maxwidth=400&photoreference={photo_reference}&key={api_key}"

# Display the page
def display_clubs_page():
    # Header
    st.markdown('<div class="header">Clubs Page</div>', unsafe_allow_html=True)

    # Location input (City, Zip Code, or Neighborhood)
    location_input = st.text_input("Enter any location (e.g. A 79936, Austin TX, udistrict)")

    if location_input:
        location = location_input
        st.markdown(f'<div class="location-display">📍 {location}</div>', unsafe_allow_html=True)

        # Categories to search (gyms, fitness clubs, dance studios)
        categories = ["gyms", "fitness clubs", "dance studios", "pilates clubs"]

        # Set to track already displayed places (avoiding duplicates)
        displayed_places = set()

        # Container for club listings
        container = st.container()

        with container:
            for category in categories:
                query = f"{category} in {location}"
                places = find_places(query, API_KEY)

                if places:
                    for idx, place in enumerate(places[:5]):  # limit results to 5
                        place_id = place.get("place_id")
                        
                        # Skip if the place has already been displayed
                        if place_id in displayed_places:
                            continue
                        
                        displayed_places.add(place_id)  # Mark place as displayed

                        name = place.get("name")
                        address = place.get("formatted_address")
                        rating = place.get("rating", "N/A")
                        photo_reference = place.get("photos", [{}])[0].get("photo_reference")

                        # Create the expander for each club
                        with st.expander(f"{name} | {address}"):
                            cols = st.columns([1, 3])

                            # Left column for logo and buttons
                            with cols[0]:
                                if photo_reference:
                                    photo_url = get_photo_url(photo_reference, API_KEY)
                                    st.image(photo_url, width=100, use_container_width=True)

                                # Make the button keys unique by adding both the category and idx
                                st.button("Follow", key=f"{category}_follow_{idx}")
                                st.button("Join", key=f"{category}_join_{idx}")

                            # Right column for details
                            with cols[1]:
                                st.subheader(name)
                                st.write(f"📍 **{address}**")
                                details = get_place_details(place_id, API_KEY)
                                hours = details.get("opening_hours", {}).get("weekday_text", [])
                                if hours:
                                    st.write("🕒 **Hours**:")
                                    for line in hours:
                                        st.write(f"- {line}")
                                else:
                                    st.write("🕒 Hours not available")

                                st.write("---")

if __name__ == '__main__':
    display_clubs_page()