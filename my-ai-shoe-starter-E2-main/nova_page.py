import streamlit as st
from google.genai import types
from nova_backend import call_nova        
from mimetypes import guess_type

# st.set_page_config(page_title="Nova", layout="wide")
def handle_send(uploaded_file):
    message_to_send = st.session_state.user_input.strip()
    if not message_to_send:
        return

    st.session_state.messages.append(("user", message_to_send))

    parts = []
    for sender, msg in st.session_state.messages:
        role = "user" if sender == "user" else "model"
        parts.append(types.Content(role=role, parts=[types.Part.from_text(text=msg)]))

    #Handle image if uploaded
    if uploaded_file:
        mime_type, _ = guess_type(uploaded_file.name)
        if mime_type is None:
            mime_type = "image/jpeg"
        image_part = types.Part(
            inline_data=types.Blob(
                mime_type=mime_type,
                data=uploaded_file.read()
            )
        )
        parts[-1].parts.append(image_part)

    with st.spinner("Nova is typing..."):
        try:
            response = call_nova(parts)
        except Exception as e:
            response = f"⚠️ Oops! Nova had a problem: {e}"

    st.session_state.messages.append(("nova", response))
    st.session_state.user_input = ""  
    

def display_nova():
    #Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
        
    #CSS Styling
    st.markdown("""
    <style>
        .main {
            font-family: 'Segoe UI', sans-serif;
        }

        .header {
            font-size: 38px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #4B2E83;
        }

        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 20px;
            margin-bottom: 80px;
        }

        .bubble-user, .bubble-nova {
            animation: fadeIn 0.6s ease forwards;
            opacity: 0;
        }

        .bubble-user {
            align-self: flex-end;
            background: #d1ecf1;
            color: #0c5460;
            padding: 12px 16px;
            border-radius: 18px 18px 0 18px;
            max-width: 70%;
            font-size: 16px;
            box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
        }

        .bubble-nova {
            align-self: flex-start;
            background: linear-gradient(to right, #fce3ec, #ffe6f7);
            color: #4b2e83;
            padding: 12px 16px;
            border-radius: 18px 18px 18px 0;
            max-width: 70%;
            font-size: 16px;
            box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .typing {
            font-style: italic;
            font-size: 14px;
            color: #777;
            margin-left: 5px;
        }

        .sidebar .sidebar-content {
            background-color: #f7f5fc;
        }
    </style>
    """, unsafe_allow_html=True)
        
    #Intro message
    if not st.session_state.messages:
        st.session_state.messages.append(("nova", "✨ Hi there! I’m Nova, your AI fitness coach. How much time do you have for a workout today?"))

    #Page Header
    st.markdown('<div class="header">Nova</div>', unsafe_allow_html=True)

    #Chat Bubbles
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for sender, msg in st.session_state.messages:
        bubble_class = "bubble-user" if sender == "user" else "bubble-nova"
        st.markdown(f'<div class="{bubble_class}">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.text_input(
        " ",
        placeholder="Type your message to Nova...",
        key="user_input",
        on_change=lambda: handle_send(uploaded_file)
    )

    uploaded_file = st.file_uploader(
        "Drag and drop image here",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

    if st.button("Clear Chat"):
        st.session_state.messages = []
    
    




