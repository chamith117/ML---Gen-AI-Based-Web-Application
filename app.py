import streamlit as st
from screens.loading_screen import loading_screen
from screens.login_screen import login_screen
from screens.travel_screen import travel_screen
from screens.view_flight import view_flight_screen

# Initialize session state for screen navigation
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'loading'  # Start with loading screen

# Navigation based on the current screen in session state
if st.session_state.current_screen == 'loading':
    loading_screen()

elif st.session_state.current_screen == 'login':
    login_screen()

elif st.session_state.current_screen == 'travel':
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        travel_screen()
    else:
        st.error("Please log in first.")
        st.session_state.current_screen = 'login'
        st.experimental_rerun()

elif st.session_state.current_screen == 'view_flight':
    view_flight_screen()
