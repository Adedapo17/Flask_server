import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Coordinates for Ilorin, Kwara State, Nigeria
latitude = 8.44
longitude = 4.494

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Function to fetch historical weather data from Open-Meteo API
def fetch_weather_data(date):
    """
    Fetches historical weather data for a specific date from the Open-Meteo API.

    Parameters:
    - date (str): Date in 'YYYY-MM-DD' format for which to fetch the data.

    Returns:
    - dict: A dictionary containing weather data for the specified date.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max", "temperature_2m_mean"],
        "timezone": "Africa/Lagos"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # Process daily data
    daily = response.Daily()
    
    # Extract the necessary weather data
    weather_data = {
        "T2M_MAX": daily.Variables(0).ValuesAsNumpy()[0],  # temperature_2m_max
        "T2M_MIN": daily.Variables(1).ValuesAsNumpy()[0],  # temperature_2m_min
        "WS2M_MAX": daily.Variables(2).ValuesAsNumpy()[0],  # wind_speed_10m_max
        "T2M": daily.Variables(3).ValuesAsNumpy()[0],      # temperature_2m_mean
    }
    
    return weather_data

# Function to predict future temperatures and calculate GDD
def predict_future_temperatures_and_gdd(model_max, model_min, weather_data, base_temp=10):
    """
    Predict future max and min temperatures and calculate GDD (Growing Degree Days).
    
    Parameters:
    - model_max: Trained Ridge regression model for max temperature.
    - model_min: Trained Ridge regression model for min temperature.
    - weather_data: Dictionary containing the weather predictors.
    - base_temp: Base temperature for GDD calculation.
    
    Returns:
    - dict: Predictions including max temp, min temp, and GDD.
    """
    # Convert predictors_values to DataFrame with proper feature names
    predictors_values = pd.DataFrame([[
        weather_data["T2M_MAX"],
        weather_data["T2M_MIN"],
        weather_data["WS2M_MAX"],
        weather_data["T2M"]
    ]], columns=["T2M_MAX", "T2M_MIN", "WS2M_MAX", "T2M"])

    # Predict max and min temperatures
    predicted_max = model_max.predict(predictors_values)[0]
    predicted_min = model_min.predict(predictors_values)[0]

    # Calculate GDD
    gdd = max(((predicted_max + predicted_min) / 2) - base_temp, 0)

    # Return predictions
    return {
        'predicted_max': predicted_max,
        'predicted_min': predicted_min,
        'GDD': gdd
    }

# Load the dataset
data = pd.read_csv("daily climate data.csv", index_col="DATE")

# Clean the data by dropping rows with missing values
data.dropna(inplace=True)

# Convert the 'DATE' column to datetime and set it as index
data.index = pd.to_datetime(data.index, dayfirst=True)

# Shift the target values to create predictions for the next year
data['target_max'] = data["T2M_MAX"].shift(-365)
data['target_min'] = data["T2M_MIN"].shift(-365)

# Drop rows with NaN target values due to the shift
data.dropna(inplace=True)

# Train the Ridge regression models
reg_max = Ridge(alpha=0.1)
reg_min = Ridge(alpha=0.1)
predictors = ["T2M_MAX", "T2M_MIN", "WS2M_MAX", "T2M"]

train = data.loc[:"2019-12-31"]
reg_max.fit(train[predictors], train['target_max'])
reg_min.fit(train[predictors], train['target_min'])
