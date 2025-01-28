import streamlit as st
from datetime import timedelta

def view_flight_screen():
    st.title("View Flights")

    # Retrieve the stored data from session state
    if 'starting_country' in st.session_state:
        starting_country = st.session_state.starting_country
        destination_country = st.session_state.destination_country
        travel_date = st.session_state.travel_date
        travelers = st.session_state.travelers
        days = st.session_state.days
    else:
        st.error("No travel data found. Please go back and enter travel details.")
        return

    st.write(f"Starting Country: {starting_country}")
    st.write(f"Destination Country: {destination_country}")
    st.write(f"Travel Date: {travel_date.strftime('%Y-%m-%d')}")
    st.write(f"Number of Travelers: {travelers}")
    st.write(f"Return Date: {(travel_date + timedelta(days=days)).strftime('%Y-%m-%d')}")

    # Add inputs for flight search
    departure_time = st.selectbox('Select Preferred Departure Time', ['Morning', 'Afternoon', 'Evening', 'Night'])
    flight_class = st.selectbox('Select Flight Class', ['Economy', 'Business', 'First Class'])

    # Search flights button
    if st.button("Search Flights"):
        st.write(f"Searching flights from {starting_country} to {destination_country}...")
        st.write(f"Departure Date: {travel_date.strftime('%Y-%m-%d')}")
        st.write(f"Preferred Time: {departure_time}")
        st.write(f"Class: {flight_class}")
        # Here, you can add the logic to fetch flight details from an API or database
