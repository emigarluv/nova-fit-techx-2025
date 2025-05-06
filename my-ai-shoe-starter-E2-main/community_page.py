import streamlit as st
from data_fetcher import get_user_profile, get_user_posts, get_genai_advice
from modules import display_activity_summary, display_recent_workouts, display_genai_advice, display_post

def display_community_page(user_id):
   
    # --- Fetch Data ---
    user = get_user_profile(user_id)
    posts = []

    for friend_id in user['friends']:
        friend = get_user_profile(friend_id)
        posts += get_user_posts(friend['user_id'])

    posts = sorted(posts, key=lambda p: p['timestamp'], reverse=True)[:10]
    advice = get_genai_advice(user_id)


    # --- Styling (App Color Theme) ---
    st.markdown("""
    <style>
        body { background-color: #F0EEE3; }

        .header {
            text-align: center;
            font-size: 48px;
            font-weight: 800;
            color: #3D3E3E;
            margin-top: 10px;
        }

        .subtext {
            text-align: center;
            color: #555;
            margin-bottom: 20px;
        }

        .motivation-box {
            background-color: #B8DAC3;
            padding: 20px;
            border-radius: 10px;
            font-weight: bold;
            color: #3D3E3E;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
        }

        .section-title {
            font-size: 28px;
            font-weight: bold;
            color: #E26A3F;
            margin-top: 30px;
        }

        .post-box {
            background-color: #FFFFFF;
            border-left: 6px solid #E79D62;
            padding: 16px;
            margin: 12px 0;
            border-radius: 10px;
            box-shadow: 1px 1px 6px rgba(0,0,0,0.07);
        }

        .username {
            font-weight: 700;
            color: #4EA09D;
        }

        .timestamp {
            font-size: 12px;
            color: #999;
            margin-bottom: 5px;
        }

        .no-image {
            color: #AAA;
            font-style: italic;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Title ---
    st.markdown("<div class='header'>🌐 Community Page</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtext'>Welcome, <b>{user['full_name']}</b> (@{user['username']}) 👋</div>", unsafe_allow_html=True)

    # --- GenAI Advice ---
    st.markdown("<h2 class='section-title'>💡 Daily Motivation</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='motivation-box'>{advice['content']}</div>", unsafe_allow_html=True)
    if advice['image']:
        st.image(advice['image'])

    # --- Friends' Posts ---
    st.markdown("<h2 class='section-title'>💬 Friends' Posts</h2>", unsafe_allow_html=True)
    if not posts:
        st.info("No posts from friends yet.")
    else:
        for post in posts:
            profile = get_user_profile(post['user_id'])
            display_post(profile['username'], profile['profile_image'], post['timestamp'], post['content'], post['image'])
            
# Run
if __name__ == "__main__":
    display_community_page('user1')
       
