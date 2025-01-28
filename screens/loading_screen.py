import streamlit as st
import time
import os

def loading_screen():
    # Get the absolute path of the GIF file
    file_path = os.path.join(os.path.dirname(__file__), 'Black Simple Travel Logo.gif')
    
    # Display GIF
    try:
        with open(file_path, 'rb') as gif_file:
            st.image(gif_file.read(), use_column_width=True)
    except FileNotFoundError:
        st.error("GIF file not found. Please check the file path.")

    # Create a loading bar that lasts for 5 seconds
    progress_bar = st.progress(0)
    for percent_complete in range(100):
        time.sleep(0.05)  # 0.05 sec * 100 = 5 sec total
        progress_bar.progress(percent_complete + 1)

    # After loading is done, transition to the login screen
    st.session_state.current_screen = 'login'
    st.experimental_rerun()

# Call the loading screen function
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = 'loading'

if st.session_state.current_screen == 'loading':
    loading_screen()
