from modules import display_post
import streamlit as st
from data_fetcher import get_user_workouts, get_user_posts
from google.cloud import bigquery
from datetime import datetime
from modules import format_date
import uuid

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'

def display_post_cards(posts_data_list):
    """
    Displays posts side-by-side using the provided display_post function.

    Args:
        posts_data_list (list): A list of dictionaries, where each dictionary
                                contains data for one post.
    """
    st.header("Activity Feed")  # Section header
    cols = st.columns(3)  # Create 3 columns

    for i, post_data in enumerate(posts_data_list[:3]):
        with cols[i]:
            if post_data and isinstance(post_data, dict):
                display_post(
                    username=post_data.get('username', 'N/A'),
                    user_image=post_data.get('user_image', ''),
                    timestamp=post_data.get('timestamp', 'N/A'),
                    content=post_data.get('content', 'No content available.'),
                    post_image=post_data.get('post_image', '')
                )
            else:
                # Maintain layout spacing even if data is missing
                st.empty()


def display_summary(workouts_list, author_id):    
    """
    Calculates and displays the workout summary (Steps, Miles, Calories)
    and Share buttons based on a list of workouts.

    Args:
        workouts_list (list): A list of dictionaries representing workouts.
    """
    total_steps = sum(w.get('steps', 0) for w in workouts_list)
    total_distance = sum(w.get('distance', 0.0) for w in workouts_list)
    total_calories = sum(w.get('calories_burned', 0) for w in workouts_list)

    formatted_steps = f"{total_steps:,}"
    formatted_distance = round(total_distance, 1)
    formatted_calories = total_calories

    st.markdown("---")
    st.subheader("Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 24px; font-weight: bold; margin-bottom: 0;">{formatted_steps}</p>
            <p style="font-size: 14px; color: grey;">Steps</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 24px; font-weight: bold; margin-bottom: 0;">{formatted_distance}</p>
            <p style="font-size: 14px; color: grey;">Miles</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 24px; font-weight: bold; margin-bottom: 0;">{formatted_calories}</p>
            <p style="font-size: 14px; color: grey;">Calories</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        if st.button("SHARE", key="share_steps", use_container_width=True):
            st.toast(f"Sharing {formatted_steps} steps!")
            create_share_post(author_id, f"I just walked {formatted_steps} steps!")

    with btn_col2:
        if st.button("SHARE", key="share_miles", use_container_width=True):
            st.toast(f"Sharing {formatted_distance} miles!")
            create_share_post(author_id, f"I just went {formatted_distance} miles!")

    with btn_col3:
        if st.button("SHARE", key="share_calories", use_container_width=True):
            st.toast(f"Sharing {formatted_calories} calories!")
            create_share_post(author_id, f"I just burned {formatted_calories} calories!")

def create_share_post(author_id, content, image_url=""):
    """Inserts a new share post into the BigQuery table."""
    client = bigquery.Client(project=project_id)
    post_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    table_id = f"{project_id}.{dataset_id}.{posts_table}"

    rows_to_insert = [{
        "PostId": post_id,
        "AuthorId": author_id,
        "Timestamp": timestamp,
        "ImageUrl": "",
        "Content": content
    }]

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Failed to insert post: {errors}")
        return False
    return True


def fetch_latest_posts(limit=3):
    """Fetches the most recent posts from BigQuery."""
    client = bigquery.Client(project=project_id)

    query = f"""
        SELECT AuthorId, Timestamp, ImageUrl, Content
        FROM `{project_id}.{dataset_id}.{posts_table}`
        ORDER BY Timestamp DESC
        LIMIT @limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit)
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        rows = query_job.result()

        posts_data = []
        for row in rows:
            posts_data.append({
                "username": row.AuthorId,
                "user_image": "",  # You could add lookup logic for user image here
                "timestamp": str(row.Timestamp),
                "post_image": "",
                "content": row.Content or "No content available."
            })

        return posts_data

    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []

project_id = "egarcia154techx25"
dataset_id = "ISE"
posts_table = "Posts"

def display_activity_page(user_id, workouts_list, posts_data_list):
    """
    Main function to render the activity page layout.

    Args:
        user_id (str or int): ID of the current user (used for sharing).
        workouts_list (list): Workout data.
        posts_data_list (list): Recent post data.
    """
    display_post_cards(posts_data_list)
    display_summary(workouts_list, user_id)


# --- MAIN PAGE RENDERING ---

def main():
    user_id = 1  # Replace with actual logged-in user ID logic
    workouts_list = get_user_workouts(user_id)

    latest_posts = fetch_latest_posts(limit=3)
    display_activity_page(user_id, workouts_list, latest_posts)


if __name__ == "__main__":
    main()