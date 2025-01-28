import streamlit as st
import requests
import json
import time  # For adding the delay
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("fnl-4fad6-firebase-adminsdk-lovi2-be32da0a06.json")
    firebase_admin.initialize_app(cred)

# Firebase Web API Key provided
FIREBASE_WEB_API_KEY = "AIzaSyBMhqFnbZQWR9L_EylDwgFDRCziWIZGRHc"

def login_screen():
    # Injecting custom CSS for better design
    st.markdown("""
        <style>
        /* Center the form */
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 50px;
            background-color: #f9f9f9;
            border-radius: 15px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        
        /* Style the title */
        .login-title {
            text-align: center;
            font-size: 36px;
            color: #007BFF;
            margin-bottom: 40px;
            font-weight: bold;
        }

        /* Style the form elements */
        .login-label {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .login-input {
            padding: 10px;
            width: 100%;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        /* Style the button */
        .login-button {
            background-color: #007BFF;
            color: white;
            padding: 10px;
            width: 100%;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
        }

        .login-button:hover {
            background-color: #0056b3;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-title'>Welcome!</div>", unsafe_allow_html=True)

    # Create a container for the login/register form
    st.markdown("<div class='login'>", unsafe_allow_html=True)

    # Create tabs for Login and Register
    tabs = st.tabs(["Login", "Register"])

    # Firebase REST API endpoint for logging in
    firebase_login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"

    with tabs[0]:  # Login tab
        st.subheader("Login")
        email = st.text_input("Email", key="login_email", help="Enter your email address")
        password = st.text_input("Password", type='password', key="login_password", help="Enter your password")

        if st.button("Login", key="login_button", help="Log in with your credentials"):
            # Prepare the payload for REST API login request
            payload = json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": True
            })

            try:
                # Send a POST request to Firebase's REST API for login
                response = requests.post(firebase_login_url, data=payload)
                response_data = response.json()

                # Check if login was successful
                if "idToken" in response_data:
                    st.session_state.authenticated = True
                    st.success(f"Login successful! Welcome {email}")
                    time.sleep(2)  # Add a 2-second loading delay
                    st.session_state.current_screen = 'travel'  # Move to the travel screen
                    st.experimental_rerun()  # Rerun the app to go to the travel screen
                else:
                    st.error(response_data.get("error", {}).get("message", "Login failed"))

            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    with tabs[1]:  # Register tab
        st.subheader("Register")
        email = st.text_input("Email", key="register_email", help="Enter your email address")
        password = st.text_input("Password", type='password', key="register_password", help="Enter your password")

        if st.button("Register", key="register_button", help="Create a new account"):
            try:
                # Create a new user with Firebase Admin SDK
                user = auth.create_user(
                    email=email,
                    password=password  # Firebase Admin SDK allows creating users with passwords
                )
                st.success(f"User registered successfully! You can now log in with {user.email}")
            except Exception as e:
                st.error(f"Registration failed: {e}")

    # Close the container
    st.markdown("</div>", unsafe_allow_html=True)
