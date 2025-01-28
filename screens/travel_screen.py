import streamlit as st
import joblib
import numpy as np
import cohere
import requests
from datetime import datetime
import os
import firebase_admin
from firebase_admin import credentials

def travel_screen():
    st.title("TRIP PLANNER IN SOUTHEAST ASIA")

    # Initialize Firebase Admin SDK if not already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate("fnl-4fad6-firebase-adminsdk-lovi2-be32da0a06.json")
        firebase_admin.initialize_app(cred)

    # Initialize Cohere API for travel plan generation
    COHERE_API_KEY = "OYGMt2d1rK1UHcr4L6auOyAQyhoGljSBUbaMiyPz"  # Replace with your Cohere API key
    co = cohere.Client(COHERE_API_KEY)

    # Load the trained cost prediction model
    model_file = 'trained_travel_cost_model_v5.pkl'

    if os.path.exists(model_file):
        model = joblib.load(model_file)
    else:
        st.error(f"Model file not found: {model_file}")
        st.stop()

    # Custom CSS for the dashboard look
    st.markdown("""
        <style>
            .dashboard-title {
                font-size: 36px;
                font-weight: bold;
                color: #007BFF;
                text-align: center;
                margin-bottom: 20px;
            }
            .card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                text-align: center;
            }
            .card-title {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }
            .card-value {
                font-size: 28px;
                font-weight: bold;
                color: #007BFF;
            }
            .exchange-rate-box {
                background-color: #e9f5e9;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #28a745;
                margin-bottom: 20px;
                text-align: center;
            }
            .exchange-rate {
                color: #28a745;
                font-weight: bold;
            }
            .day-container {
                background-color: #f0f9ff;
                border: 1px solid #d1e7f5;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 8px;
            }
            .day-title {
                color: #0056b3;
                font-weight: bold;
                font-size: 20px;
                margin-bottom: 5px;
            }
            .details {
                color: #333;
                font-size: 16px;
            }
            .aligned-box {
                display: flex;
                justify-content: center;
                align-items: center;
            }
        </style>
    """, unsafe_allow_html=True)

    # Function to preprocess input for cost prediction
    def preprocess_input(country, preferences, days, travelers, package):
        country_encoding = [0, 0, 0]
        preference_encoding = [0, 0, 0, 0, 0]
        package_encoding = [0, 0]
        extra_features = [0, 0]

        country_map = {'Malaysia': 0, 'Thailand': 1, 'Singapore': 2}
        preference_map = {'Beach': 0, 'Adventure': 1, 'Cultural': 2, 'Nature': 3, 'Shopping': 4}

        if country in country_map:
            country_encoding[country_map[country]] = 1

        if preferences:
            for pref in preferences:
                if pref in preference_map:
                    preference_encoding[preference_map[pref]] = 1

        if package == 'Budget':
            package_encoding = [0, 0]
        elif package == 'Mid-Range':
            package_encoding = [1, 0]
        elif package == 'Premium':
            package_encoding = [0, 1]

        input_vector = np.array(country_encoding + preference_encoding + [days, travelers] + package_encoding + extra_features).reshape(1, -1)
        return input_vector

    # Function to get exchange rates
    def get_exchange_rates():
        rates = {
            "LKR": 330,
            "MYR": 4.18,
            "THB": 33.50,
            "SGD": 1.36
        }
        return rates

    # Function to fetch weather information from OpenWeather API
    def get_weather(city):
        api_key = "4bd14efe9d87f04e546b7722cf4f6071"  # Replace with your OpenWeather API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            return weather_desc, temp, humidity
        else:
            return None, None, None

    # Function to get weather for all major airports based on the selected country
    def get_airport_weather(country):
        airports = {
            'Malaysia': ['Kuala Lumpur', 'Penang', 'Johor Bahru'],
            'Thailand': ['Bangkok', 'Phuket', 'Chiang Mai'],
            'Singapore': ['Singapore Changi']
        }
        airport_weather = {}

        if country in airports:
            for airport in airports[country]:
                weather_desc, temp, humidity = get_weather(airport)
                if weather_desc:
                    airport_weather[airport] = (weather_desc, temp, humidity)
        
        return airport_weather
    
    # Function to fetch flight prices from Sri Lanka to the selected country
    def get_flight_prices(destination):
        api_key = "3e36c9d5094fd8779228dacb890a5b8e"  # Replace with your AviationStack API key
        base_url = "http://api.aviationstack.com/v1/flights"
        
        params = {
            'access_key': api_key,
            'dep_iata': 'CMB',  # IATA code for Bandaranaike International Airport, Sri Lanka
            'arr_iata': destination,
            'limit': 1
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Check if flight data is available
            if 'data' in data and len(data['data']) > 0:
                flight_info = data['data'][0]
                
                # Attempt to get the price, airline, and flight number
                airline = flight_info.get('airline', {}).get('name', 'Unknown Airline')
                flight_number = flight_info.get('flight', {}).get('number', 'N/A')
                price = flight_info.get('price', 'Price Not Available')  # Replace with actual price field
                
                return f"{airline} Flight {flight_number}: {price} USD"
            else:
                return "No flight data available for the selected destination."
        else:
            return "Failed to fetch flight prices."



    # Generate AI travel plan
    def generate_travel_plan(country, travel_days, traveler_count, travel_date):
        prompt = (
            f"Create a detailed {travel_days}-day travel itinerary for {traveler_count} people visiting {country}, "
            f"starting from {travel_date}. Each day's summary should mention a main attraction, a dining recommendation, "
            f"and one additional activity, along with transportation options for the day. Keep the descriptions concise and focus on key highlights."
        )

        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=5500
        )

        if response.generations:
            travel_plan = response.generations[0].text.strip()
            return travel_plan
        else:
            return "Error: Unable to generate a travel plan"

    # User inputs
    country = st.selectbox('🌍 Select Country', ['Malaysia', 'Thailand', 'Singapore'])
    preferences = st.multiselect('🎒 Select Travel Preferences', ['Beach', 'Adventure', 'Cultural', 'Nature', 'Shopping'])
    days = st.slider('📅 Number of Travel Days', min_value=3, max_value=21, value=7)
    travelers = st.slider('👥 Number of Travelers', min_value=1, max_value=10, value=2)
    package = st.selectbox('🏷️ Select Travel Package', ['Budget', 'Mid-Range', 'Premium'])
    travel_date = st.date_input('📅 Select Travel Start Date', value=datetime.now())

    # Predict button (combined)
    if st.button('Get Started'):
        custom_input = preprocess_input(country, preferences, days, travelers, package)
        prediction = model.predict(custom_input)[0]

        # Apply package adjustments
        if package == 'Mid-Range':
            prediction *= 1.20
        elif package == 'Premium':
            prediction *= 1.50

        # Adjust for travel days
        if days != 7:
            prediction *= (days / 7)

        # Get exchange rates
        exchange_rates = get_exchange_rates()

        # Display results in a dashboard format
        col1, col2, col3 = st.columns(3)

        # Card 1: Total Estimated Cost in USD
        with col1:
            st.markdown('<div class="card aligned-box">', unsafe_allow_html=True)
            st.write(f"<div class='card-title'>Cost per Person (USD)</div>", unsafe_allow_html=True)
            st.write(f"<div class='card-value'>${prediction:.2f}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Convert to LKR
        cost_lkr = prediction * exchange_rates["LKR"]
        with col2:
            st.markdown('<div class="card aligned-box">', unsafe_allow_html=True)
            st.write(f"<div class='card-title'>Cost per Person (LKR)</div>", unsafe_allow_html=True)
            st.write(f"<div class='card-value'>Rs {cost_lkr:.2f}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Convert to local currency (MYR/THB/SGD)
        local_currency = {'Malaysia': 'MYR', 'Thailand': 'THB', 'Singapore': 'SGD'}[country]
        cost_local_currency = prediction * exchange_rates[local_currency]
        with col3:
            st.markdown('<div class="card aligned-box">', unsafe_allow_html=True)
            st.write(f"<div class='card-title'>Cost per Person ({local_currency})</div>", unsafe_allow_html=True)
            st.write(f"<div class='card-value'>{cost_local_currency:.2f} {local_currency}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Exchange Rate Box
        st.markdown('<div class="exchange-rate-box aligned-box">', unsafe_allow_html=True)
        st.write(f"💱 **Exchange Rates**")
        st.write(f"1 USD = {exchange_rates['LKR']} LKR")
        st.write(f"1 USD = {exchange_rates['MYR']} MYR")
        st.write(f"1 USD = {exchange_rates['THB']} THB")
        st.write(f"1 USD = {exchange_rates['SGD']} SGD")
        st.markdown('</div>', unsafe_allow_html=True)

        # Total cost for all travelers
        col1, col2, col3 = st.columns(3)

        # Total Cost in USD
        total_cost_usd = prediction * travelers
        with col1:
            st.markdown('<div class="card aligned-box">', unsafe_allow_html=True)
            st.write(f"<div class='card-title'>Total Cost for {travelers} Travelers (USD)</div>", unsafe_allow_html=True)
            st.write(f"<div class='card-value'>${total_cost_usd:.2f}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Total Cost in LKR
        total_cost_lkr = cost_lkr * travelers
        with col2:
            st.markdown('<div class="card aligned-box">', unsafe_allow_html=True)
            st.write(f"<div class='card-title'>Total Cost for {travelers} Travelers (LKR)</div>", unsafe_allow_html=True)
            st.write(f"<div class='card-value'>Rs {total_cost_lkr:.2f}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Total Cost in Local Currency
        total_cost_local_currency = cost_local_currency * travelers
        with col3:
            st.markdown('<div class="card aligned-box">', unsafe_allow_html=True)
            st.write(f"<div class='card-title'>Total Cost for {travelers} Travelers ({local_currency})</div>", unsafe_allow_html=True)
            st.write(f"<div class='card-value'>{total_cost_local_currency:.2f} {local_currency}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Fetch and display weather for major airports
        airport_weather = get_airport_weather(country)
        st.write(f"## ✈️ Major Airport Weather in {country}")
        for airport, (desc, temp, humidity) in airport_weather.items():
            st.markdown(f"""
                <div class="card aligned-box" style="border: 1px solid #ccc; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 20px;">
                    <div class="card-header" style="padding: 10px; border-radius: 10px 10px 0 0; display: flex; align-items: center;">
                        <span style="margin-right: 10px; font-size: 24px;">✈️</span>
                        <h4 style="margin: 0; font-size: 18px; color: #333;">{airport} Airport</h4>
                    </div>
                    <div class="card-body" style="padding: 15px; background-color: #f9f9f9; border-radius: 0 0 10px 10px;">
                        <div style="font-size: 18px; color: #0056b3; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center;">
                            <span style="margin-right: 8px; font-size: 20px;">☁️</span>
                            Description: {desc.capitalize()}
                        </div>
                        <div style="font-size: 16px; color: #333; margin-bottom: 5px; display: flex; align-items: center;">
                            <span style="margin-right: 8px; font-size: 18px;">🌡️</span>
                            <span style="font-weight: bold;">Temperature:</span> {temp} °C
                        </div>
                        <div style="font-size: 16px; color: #333; display: flex; align-items: center;">
                            <span style="margin-right: 8px; font-size: 18px;">💧</span>
                            <span style="font-weight: bold;">Humidity:</span> {humidity}%
                        </div>
                    </div>
                </div>

            """, unsafe_allow_html=True)

        # Get flight prices from Sri Lanka to the selected country
        flight_price_info = get_flight_prices(country)

        # Display flight price card
        st.markdown(f"""
            <div class="card aligned-box">
                <div class="card-title">Flight Price from Sri Lanka to {country}</div>
                <div class="card-value">{flight_price_info}</div>
            </div>
        """, unsafe_allow_html=True)

                

        # Generate travel plan
        travel_plan = generate_travel_plan(country, days, travelers, travel_date)
        st.write(f"## 📝 Travel Plan for {country}")

        # Split the generated plan by day and format it
        days_plan = travel_plan.split('Day ')
        days_plan = [f'Day {day.strip()}' for day in days_plan if day.strip()]

        for day in days_plan:
            st.markdown(f"""
                <div class="day-container">
                    <div class="day-title">{day.split(':')[0]}</div>
                    <div class="details">{day[len(day.split(':')[0])+1:].strip()}</div>
                </div>
            """, unsafe_allow_html=True)

